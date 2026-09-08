/* strategy.js - ETF/指数化趋势跟随：唐奇安通道 + ATR波动率头寸管理
 *
 * 方案选择：方案二——经典唐奇安通道 + ATR头寸管理（海龟交易变种）。
 *
 * 理论依据：海龟交易法则的核心是“用价格突破识别趋势、用通道反向突破退出”，
 * 属于经典时间序列动量/趋势跟随框架；ATR仓位管理进一步让每笔交易承担近似
 * 稳定的波动风险，波动越大，下单数量越少。相比个股回调低吸，它不依赖 RSI
 * 在强趋势中频繁触发，更适合流动性较好的ETF，并能在震荡期通过通道止损控制损失。
 *
 * 本文件只改变指标和交易信号；T+1、账户8%硬熔断、个股/ETF单日8%止损、
 * ATR移动止损、手续费、印花税与滑点等风控底座保持不变。
 */
export const DEFAULT_CONFIG = {
  initialCapital: 1_000_000, years: 2,
  // 当前 data_loader.js 对深市代码的映射最稳妥，选用流动性较好的深市ETF池。
  symbols: ['159915', '159949', '159928', '159941'],
  donchianEntryPeriod: 20, donchianExitPeriod: 10,
  atrPeriod: 14, atrStopMultiple: 2,
  // 每笔交易最多承担账户资金的1%，同时受单标的20%名义仓位上限约束。
  riskPerTradePct: 0.01, maxPositionPct: 0.20,
  dailyLossLimit: 0.08, maxDrawdown: 0.08,
  commissionRate: 0.0003, stampTaxRate: 0.001, slippageRate: 0.0005,
  riskFreeRate: 0.025, lotSize: 100, forceExitAtClose: true
};

const sma = (a, p, i) => i + 1 < p ? null : a.slice(i - p + 1, i + 1).reduce((x, y) => x + y, 0) / p;
const maxPrior = (a, p, i) => i < p ? null : Math.max(...a.slice(i - p, i));
const minPrior = (a, p, i) => i < p ? null : Math.min(...a.slice(i - p, i));

export function addIndicators(bars, c) {
  const trs = [];
  for (let i = 0; i < bars.length; i++) {
    const prev = i ? bars[i - 1].close : bars[i].close;
    trs.push(Math.max(
      bars[i].high - bars[i].low,
      Math.abs(bars[i].high - prev),
      Math.abs(bars[i].low - prev)
    ));
  }
  return bars.map((b, i) => ({
    ...b,
    // 排除当日数据，避免用当日最高/最低价构造当日突破，造成未来函数。
    donchianHigh: maxPrior(bars.map(x => x.high), c.donchianEntryPeriod, i),
    donchianLow: minPrior(bars.map(x => x.low), c.donchianExitPeriod, i),
    atr: i + 1 < c.atrPeriod ? null : sma(trs, c.atrPeriod, i)
  }));
}

export class BacktestStrategy {
  constructor(config) {
    this.c = config;
    this.position = null;
    this.cash = config.initialCapital;
    this.equityPeak = config.initialCapital;
    this.halted = false;
    this.trades = [];
  }
  order_target_percent(symbol, targetPct, price, date) { return { symbol, targetPct, price, date }; }
  value(price) { return this.cash + (this.position ? this.position.qty * price : 0); }

  executeSell(bar, reason) {
    if (!this.position) return;
    const p = this.position;
    const price = bar.open * (1 - this.c.slippageRate);
    const gross = p.qty * price;
    this.cash += gross * (1 - this.c.commissionRate - this.c.stampTaxRate);
    this.trades.push({
      symbol: p.symbol, entryDate: p.entryDate, exitDate: bar.date,
      entry: p.entryPrice, exit: price, qty: p.qty,
      pnl: (price - p.entryPrice) * p.qty, reason
    });
    this.order_target_percent(p.symbol, 0, price, bar.date);
    this.position = null;
  }

  onBar(symbol, bars, i, marketBars = this.c.marketBars) {
    const b = bars[i], prev = i ? bars[i - 1] : null;
    const equity = this.value(b.close);
    this.equityPeak = Math.max(this.equityPeak, equity);

    // 账户硬熔断：保持原有8%最大回撤规则。
    if (equity < this.equityPeak * (1 - this.c.maxDrawdown)) {
      this.halted = true;
      if (this.position) this.executeSell(b, '账户最大回撤熔断');
      return;
    }

    if (this.position) {
      // A股/ETF T+1：买入当天不卖出。
      if (this.position.entryDate === b.date) return;

      // ATR追踪止损只上移不下移。
      this.position.stop = Math.max(
        this.position.stop,
        b.close - this.c.atrStopMultiple * (b.atr || 0)
      );
      // 通道下轨随新K线更新，跌破最近10日最低价即退出。
      if (b.donchianLow != null) this.position.exitChannel = b.donchianLow;
      const dailyStop = prev && b.close <= prev.close * (1 - this.c.dailyLossLimit);
      const channelExit = this.position.exitChannel != null && b.low <= this.position.exitChannel;
      if (b.low <= this.position.stop || dailyStop || channelExit) {
        this.executeSell(
          b,
          dailyStop ? '单日跌幅风控' : channelExit ? '跌破10日唐奇安下轨' : 'ATR移动止损'
        );
      }
      return;
    }

    if (this.halted || b.donchianHigh == null || b.atr == null || b.atr <= 0) return;

    // 海龟式入场：收盘突破前20个交易日最高价，不追踪当日自身高点。
    const breakout = b.close > b.donchianHigh;
    if (!breakout) return;

    // ATR风险仓位：ATR越大，按风险预算计算出的股数越少；再受20%名义仓位上限约束。
    const riskBudget = this.cash * this.c.riskPerTradePct;
    const riskPerUnit = b.atr * this.c.atrStopMultiple;
    const riskQty = Math.floor(riskBudget / riskPerUnit / this.c.lotSize) * this.c.lotSize;
    const price = b.close * (1 + this.c.slippageRate);
    const maxNotionalQty = Math.floor((this.cash * this.c.maxPositionPct) / price / this.c.lotSize) * this.c.lotSize;
    const qty = Math.min(riskQty, maxNotionalQty);

    if (qty > 0) {
      this.cash -= qty * price * (1 + this.c.commissionRate);
      this.position = {
        symbol, qty, entryDate: b.date, entryPrice: price,
        stop: price - this.c.atrStopMultiple * b.atr,
        // 固定为入场前已知的10日下轨；后续每根K线仍使用当时的历史通道值。
        exitChannel: b.donchianLow
      };
      this.order_target_percent(symbol, qty * price / this.c.initialCapital, price, b.date);
    }
  }
}
