/* backtest.js - 回测执行、ECharts交互报告与终端指标表 */
import fs from 'node:fs/promises';
import { loadSymbol, loadBenchmark } from './data_loader.js';
import { DEFAULT_CONFIG, addIndicators, BacktestStrategy } from './strategy.js';

const c = DEFAULT_CONFIG;
function pct(x) { return `${(x * 100).toFixed(2)}%`; }
function metrics(equity, trades, c) {
  const ret = equity.at(-1).value / c.initialCapital - 1;
  const years = Math.max(1, equity.length / 252);
  const annual = (1 + ret) ** (1 / years) - 1;
  let peak = equity[0].value, mdd = 0;
  for (const x of equity) { peak = Math.max(peak, x.value); mdd = Math.min(mdd, x.value / peak - 1); }
  const rs = equity.slice(1).map((x, i) => x.value / equity[i].value - 1);
  const rf = c.riskFreeRate / 252;
  const avg = rs.reduce((a, b) => a + b, 0) / (rs.length || 1);
  const sd = Math.sqrt(rs.reduce((s, x) => s + (x - avg) ** 2, 0) / (rs.length || 1));
  const wins = trades.filter(t => t.pnl > 0), losses = trades.filter(t => t.pnl <= 0);
  const avgWin = wins.reduce((s, t) => s + t.pnl, 0) / (wins.length || 1);
  const avgLoss = Math.abs(losses.reduce((s, t) => s + t.pnl, 0) / (losses.length || 1));
  return { 总收益率: pct(ret), 年化收益率: pct(annual), 最大回撤: pct(mdd),
    夏普比率: Number(((avg - rf) / (sd || 1) * Math.sqrt(252)).toFixed(2)),
    胜率: pct(wins.length / (trades.length || 1)), 盈亏比: Number((avgWin / (avgLoss || 1)).toFixed(2)), 交易次数: trades.length };
}
function safeJson(x) { return JSON.stringify(x).replace(/</g, '\\u003c'); }

function buildReport(data, file) {
  const html = `<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>A股动量突破回测报告</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5/dist/echarts.min.js"></script>
<style>
body{margin:0;background:#f4f6f8;color:#17202a;font:14px system-ui,"Microsoft YaHei",sans-serif}.wrap{max-width:1440px;margin:0 auto;padding:28px}.hero,.card{background:#fff;border:1px solid #e5e7eb;border-radius:14px;box-shadow:0 5px 18px #17202a0d}.hero{padding:24px 28px;margin-bottom:18px}.hero h1{margin:0 0 8px;font-size:26px}.muted{color:#697586}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}.card{padding:18px}.card h2{font-size:17px;margin:0 0 10px}.chart{height:560px;width:100%}table{width:100%;border-collapse:collapse}th,td{padding:10px 8px;border-bottom:1px solid #edf0f2;text-align:right}th:first-child,td:first-child{text-align:left}th{color:#697586;font-weight:600}@media(max-width:700px){.wrap{padding:12px}.chart{height:430px}}
</style></head><body><main class="wrap">
<section class="hero"><h1>A股动量突破 + 动态 ATR 风控回测报告</h1><div class="muted">数据周期：近 ${data.config.years} 年　|　初始资金：¥${data.config.initialCapital.toLocaleString()}　|　图表支持缩放、悬停和图例切换　|　💡 交互提示：将鼠标悬停在 K 线图的【买/卖】标记上，可直接查看对应的风控触发原因。</div></section>
<section class="card"><h2>净值、沪深300与标的价格</h2><div id="chart" class="chart"></div></section>
<section class="card" style="margin-top:18px"><h2>回测指标</h2><table><thead><tr><th>标的</th><th>总收益</th><th>年化收益</th><th>最大回撤</th><th>夏普</th><th>胜率</th><th>盈亏比</th><th>交易次数</th></tr></thead><tbody>${Object.entries(data.report).map(([s, r]) => `<tr><td>${s}</td><td>${r.总收益率}</td><td>${r.年化收益率}</td><td>${r.最大回撤}</td><td>${r.夏普比率}</td><td>${r.胜率}</td><td>${r.盈亏比}</td><td>${r.交易次数}</td></tr>`).join('')}</tbody></table></section>
</main><script>
const DATA=${safeJson(data.chart)};
const chart=echarts.init(document.getElementById('chart'));
const money=v=>'¥'+Number(v).toLocaleString('zh-CN',{maximumFractionDigits:2});
const markTooltip={formatter:function(p){const d=p&&p.data?p.data:{};const price=Number(d.value!=null?d.value:(d.yAxis!=null?d.yAxis:0)).toFixed(2);if(d.action==='买入开仓'){return '操作：买入开仓<br>价格：'+price;}return '操作：卖出平仓<br>触发风控：'+(d.reason||'未注明')+'<br>价格：'+price;}};
const markLabel={show:true,color:'#fff',fontWeight:'bold',formatter:function(p){return p.data.action==='买入开仓'?'买':'卖';}};
const option={animation:false,tooltip:{trigger:'axis',axisPointer:{type:'cross'}},legend:{top:4},grid:{left:65,right:70,top:42,bottom:72},dataZoom:[{type:'inside',start:0,end:100},{type:'slider',bottom:18,start:0,end:100}],xAxis:{type:'category',data:DATA.dates,boundaryGap:false},yAxis:[{type:'value',name:'净值 / 指数',scale:true},{type:'value',name:DATA.symbol+' 价格',scale:true}],series:[
{name:'策略净值',type:'line',data:DATA.strategy,smooth:false,showSymbol:false,lineStyle:{width:2,color:'#2563eb'}},
{name:'沪深300归一化',type:'line',data:DATA.benchmark,smooth:false,showSymbol:false,lineStyle:{width:2,color:'#94a3b8',type:'dashed'}},
{name:DATA.symbol+'价格',type:'line',yAxisIndex:1,data:DATA.price,smooth:false,showSymbol:false,lineStyle:{width:1.5,color:'#475569'},
 markPoint:{symbol:'pin',symbolSize:44,label:markLabel,tooltip:markTooltip,data:[
  ...DATA.buys.map(x=>({coord:[x.date,x.price],value:x.price,action:x.action||'买入开仓',itemStyle:{color:'#dc2626'},date:x.date})),
  ...DATA.sells.map(x=>({coord:[x.date,x.price],value:x.price,action:x.action||'卖出平仓',reason:x.reason||'未注明',itemStyle:{color:'#16a34a'},date:x.date}))
 ]}}
]};
chart.setOption(option);window.addEventListener('resize',()=>chart.resize());
</script></body></html>`;
  return fs.writeFile(file, html, 'utf8');
}

async function main() {
  const benchmark = await loadBenchmark(c), benchMap = new Map(benchmark.map(x => [x.date, x.close])), all = [], report = {};
  const marketBars = addIndicators(benchmark, { ...c, donchianEntryPeriod: 20, donchianExitPeriod: 10, atrPeriod: 14 });
  for (const symbol of c.symbols) {
    const d = await loadSymbol(symbol, c), bars = addIndicators(d.daily, c), s = new BacktestStrategy({ ...c, marketBars }), equity = [];
    for (let i = 0; i < bars.length; i++) { s.onBar(symbol, bars, i, marketBars); equity.push({ date: bars[i].date, value: s.value(bars[i].close) }); }
    if (s.position && c.forceExitAtClose) s.executeSell(bars.at(-1), '回测结束平仓');
    report[symbol] = metrics(equity, s.trades, c); all.push({ symbol, bars, equity, trades: s.trades });
  }
  const first = all[0], base0 = benchmark[0]?.close || 1, dates = first?.bars.map(x => x.date) || [];
  const chart = { dates, strategy: first?.equity.map(x => Number(x.value.toFixed(2))) || [], benchmark: dates.map(d => Number(((benchMap.get(d) || base0) / base0 * c.initialCapital).toFixed(2))), price: first?.bars.map(x => x.close) || [], symbol: first?.symbol || '', buys: [], sells: [] };
  for (const t of first?.trades || []) {
    const entry = first.bars.find(x => x.date === t.entryDate), exit = first.bars.find(x => x.date === t.exitDate);
    if (entry) chart.buys.push({ date: t.entryDate, price: entry.close, action: '买入开仓' });
    if (exit) chart.sells.push({ date: t.exitDate, price: exit.close, action: '卖出平仓', reason: t.reason || '未注明' });
  }
  const output = { config: c, report, results: all.map(x => ({ symbol: x.symbol, equity: x.equity, trades: x.trades })), chart };
  await fs.writeFile('backtest_report.json', JSON.stringify(output, null, 2));
  await buildReport(output, 'backtest_report.html');
  const rows = Object.entries(report).map(([symbol, r]) => ({ 标的: symbol, 总收益: r.总收益率, 年化: r.年化收益率, 最大回撤: r.最大回撤, 夏普: r.夏普比率, 胜率: r.胜率, 盈亏比: r.盈亏比, 交易次数: r.交易次数 }));
  console.log('\n=== A股动量突破回测报告 ==='); console.table(rows); console.log('已生成：backtest_report.html、backtest_report.json');
}
main().catch(e => { console.error('[致命错误]', e.stack || e); process.exitCode = 1; });
