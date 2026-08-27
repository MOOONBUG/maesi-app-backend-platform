import json
import os
from datetime import date, datetime

import pymysql
from dotenv import load_dotenv

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"), override=True)

DB = dict(
    host=os.getenv("DB_HOST", "127.0.0.1"),
    port=int(os.getenv("DB_PORT", "3306")),
    user=os.getenv("DB_USER", "rag_app"),
    password=os.getenv("DB_PASSWORD", ""),
    database=os.getenv("DB_NAME", "ai_knowledge_db"),
    charset="utf8mb4",
    cursorclass=pymysql.cursors.DictCursor,
    autocommit=False,
)

COMPANY = "迈思开源科技（演示）有限公司"
DISCLAIMER = "本数据集为完全虚构的开源演示数据，不对应任何真实企业、客户、员工或交易，可用于产品演示、开发测试与问答验收。"

SCHEMA = [
"""CREATE TABLE IF NOT EXISTS open_company_department (
 id INT PRIMARY KEY, name VARCHAR(80) NOT NULL, leader_alias VARCHAR(40) NOT NULL,
 headcount INT NOT NULL, responsibility VARCHAR(500) NOT NULL, updated_at DATETIME NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS open_company_product (
 id INT PRIMARY KEY, sku VARCHAR(32) NOT NULL UNIQUE, name VARCHAR(100) NOT NULL,
 category VARCHAR(60) NOT NULL, list_price DECIMAL(12,2) NOT NULL, status VARCHAR(20) NOT NULL,
 description VARCHAR(500) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS open_company_customer (
 id INT PRIMARY KEY, customer_code VARCHAR(32) NOT NULL UNIQUE, region VARCHAR(40) NOT NULL,
 industry VARCHAR(60) NOT NULL, customer_level VARCHAR(20) NOT NULL, public_alias VARCHAR(80) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS open_company_order_monthly (
 month CHAR(7) NOT NULL, region VARCHAR(40) NOT NULL, product_sku VARCHAR(32) NOT NULL,
 order_count INT NOT NULL, customer_count INT NOT NULL, revenue DECIMAL(14,2) NOT NULL,
 refund_amount DECIMAL(14,2) NOT NULL, PRIMARY KEY(month, region, product_sku)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS open_company_inventory (
 product_sku VARCHAR(32) PRIMARY KEY, warehouse VARCHAR(80) NOT NULL, opening_qty INT NOT NULL,
 inbound_qty INT NOT NULL, outbound_qty INT NOT NULL, available_qty INT NOT NULL,
 safety_stock INT NOT NULL, snapshot_date DATE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS open_company_finance_monthly (
 month CHAR(7) PRIMARY KEY, revenue DECIMAL(14,2) NOT NULL, cost DECIMAL(14,2) NOT NULL,
 operating_expense DECIMAL(14,2) NOT NULL, gross_profit DECIMAL(14,2) NOT NULL,
 note VARCHAR(300) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
"""CREATE TABLE IF NOT EXISTS open_company_service_monthly (
 month CHAR(7) PRIMARY KEY, ticket_count INT NOT NULL, resolved_count INT NOT NULL,
 first_response_minutes DECIMAL(8,2) NOT NULL, satisfaction_rate DECIMAL(5,2) NOT NULL,
 sla_rate DECIMAL(5,2) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4""",
]

departments = [
(1,"产品研发中心","研发负责人A",42,"负责数据平台、知识库产品、API 与质量工程",datetime(2026,8,1)),
(2,"客户成功中心","客户负责人B",18,"负责客户实施、培训、续约与服务台",datetime(2026,8,1)),
(3,"市场销售中心","销售负责人C",24,"负责华东、华南、华北和西部区域市场",datetime(2026,8,1)),
(4,"运营供应中心","运营负责人D",12,"负责采购、仓储、交付与库存管理",datetime(2026,8,1)),
(5,"综合管理中心","管理负责人E",14,"负责财务、人力、法务与行政支持",datetime(2026,8,1)),
]
products = [
(1,"MS-KB-S","企业知识库标准版","软件订阅",68000,"在售","面向中小团队的知识检索、文档问答与权限管理产品，年订阅价格"),
(2,"MS-KB-P","企业知识库专业版","软件订阅",168000,"在售","包含混合检索、审计、私有化连接器和高可用支持，年订阅价格"),
(3,"MS-DP-01","数据分析驾驶舱","数据产品",98000,"在售","提供经营指标看板、区域分析和报表导出"),
(4,"MS-API-01","智能问答 API 套餐","API服务",36000,"在售","年度基础调用套餐，超额部分按合同阶梯计费"),
(5,"MS-IMP-01","私有化实施服务","专业服务",120000,"在售","包含部署、数据清洗、权限梳理和管理员培训"),
]
customers = [
(1,"C-OPEN-001","华东","制造业","A","客户甲（匿名）"),(2,"C-OPEN-002","华东","零售业","B","客户乙（匿名）"),
(3,"C-OPEN-003","华南","物流业","A","客户丙（匿名）"),(4,"C-OPEN-004","华南","制造业","B","客户丁（匿名）"),
(5,"C-OPEN-005","华北","专业服务","A","客户戊（匿名）"),(6,"C-OPEN-006","华北","教育培训","C","客户己（匿名）"),
(7,"C-OPEN-007","西部","能源服务","B","客户庚（匿名）"),(8,"C-OPEN-008","西部","零售业","C","客户辛（匿名）"),
(9,"C-OPEN-009","华东","软件服务","A","客户壬（匿名）"),(10,"C-OPEN-010","华南","专业服务","B","客户癸（匿名）"),
]
monthly = {
"2026-01":(1180000,690000,282000),"2026-02":(980000,590000,245000),"2026-03":(1460000,830000,338000),
"2026-04":(1580000,890000,355000),"2026-05":(1710000,960000,378000),"2026-06":(1860000,1020000,405000),
"2026-07":(2040000,1110000,432000),"2026-08":(2190000,1190000,455000),
}
regions = [("华东",0.36),("华南",0.29),("华北",0.22),("西部",0.13)]
skus = [("MS-KB-S",0.24),("MS-KB-P",0.31),("MS-DP-01",0.18),("MS-API-01",0.12),("MS-IMP-01",0.15)]
order_rows=[]
for mi,(month,(revenue,_,_)) in enumerate(monthly.items(),1):
    for ri,(region,rshare) in enumerate(regions,1):
        allocated=0
        for pi,(sku,pshare) in enumerate(skus,1):
            amount=round(revenue*rshare*pshare,2)
            allocated += amount
            orders=max(1,round(amount/(48000+pi*9000)))
            customers_count=max(1,min(10,orders + ((mi+ri+pi)%2)))
            refund=round(amount*(0.004 + ((mi+ri+pi)%4)*0.002),2)
            order_rows.append((month,region,sku,orders,customers_count,amount,refund))
finance_rows=[]
for month,(revenue,cost,opex) in monthly.items():
    finance_rows.append((month,revenue,cost,opex,revenue-cost,"收入为演示确认口径；成本含云资源、交付与采购，不构成真实财务披露"))
inventory = [
("MS-KB-S","上海演示仓",18,22,25,15,10,date(2026,8,26)),("MS-KB-P","上海演示仓",12,15,17,10,8,date(2026,8,26)),
("MS-DP-01","深圳演示仓",20,18,23,15,12,date(2026,8,26)),("MS-API-01","虚拟权益仓",200,120,95,225,80,date(2026,8,26)),
("MS-IMP-01","服务产能池",16,10,12,14,8,date(2026,8,26)),
]
service=[]
for i,month in enumerate(monthly,1):
    tickets=88+i*7; resolved=tickets-(i%3); response=round(28-i*1.4,1); satisfaction=round(93.2+i*.45,2); sla=round(94.5+i*.5,2)
    service.append((month,tickets,resolved,response,satisfaction,sla))

def pct(a,b): return round(a/b*100,2) if b else 0

def build_docs():
    total_rev=sum(v[0] for v in monthly.values()); total_cost=sum(v[1] for v in monthly.values()); total_gp=total_rev-total_cost
    aug=monthly["2026-08"]; jan=monthly["2026-01"]
    region_totals={r:round(sum(float(x[5]) for x in order_rows if x[1]==r),2) for r,_ in regions}
    sku_totals={s:round(sum(float(x[5]) for x in order_rows if x[2]==s),2) for s,_ in skus}
    inv_lines=[]
    for sku,wh,opening,inbound,outbound,available,safety,snap in inventory:
        state="库存正常" if available>=safety else "低于安全库存"
        inv_lines.append(f"{sku}：可用{available}，安全库存{safety}，状态{state}，仓库{wh}")
    svc=service[-1]
    docs=[
      ("公司概况与开放数据声明",f"{COMPANY}成立于2019年，总部设于上海，定位为企业知识管理与数据分析软件服务商。演示组织总人数{sum(x[3] for x in departments)}人。主营产品包括企业知识库、数据分析驾驶舱、智能问答API和私有化实施服务。{DISCLAIMER} 数据统计截止2026-08-26。"),
      ("组织架构与部门职责（2026年8月）","；".join(f"{x[1]}：{x[3]}人，{x[4]}" for x in departments)+f"。合计{sum(x[3] for x in departments)}人。负责人均为公开演示别名。"),
      ("产品目录、SKU与公开报价", "；".join(f"{x[1]} {x[2]}：{x[3]}，公开演示报价{x[4]:,.0f}元，状态{x[5]}，{x[6]}" for x in products)+"。报价仅用于演示，不构成商业要约。"),
      ("2026年1至8月经营与财务摘要",f"2026年1-8月累计收入{total_rev:,.0f}元，累计成本{total_cost:,.0f}元，累计毛利{total_gp:,.0f}元，综合毛利率{pct(total_gp,total_rev)}%。2026年8月收入{aug[0]:,.0f}元、成本{aug[1]:,.0f}元、毛利{aug[0]-aug[1]:,.0f}元、经营费用{aug[2]:,.0f}元。1月至8月收入从{jan[0]:,.0f}元增长至{aug[0]:,.0f}元，增幅{pct(aug[0]-jan[0],jan[0])}%。所有金额均为虚构演示口径。"),
      ("2026年月度收入、成本与毛利明细","；".join(f"{m}：收入{v[0]:,.0f}元，成本{v[1]:,.0f}元，毛利{v[0]-v[1]:,.0f}元，经营费用{v[2]:,.0f}元" for m,v in monthly.items())+"。数据单位为人民币元。"),
      ("区域销售分析（2026年1至8月）","；".join(f"{r}累计收入{v:,.2f}元，占比{pct(v,total_rev)}%" for r,v in sorted(region_totals.items(),key=lambda x:x[1],reverse=True))+"。区域口径按匿名客户交付区域统计。"),
      ("产品销售结构（2026年1至8月）","；".join(f"{s}累计收入{v:,.2f}元，占比{pct(v,total_rev)}%" for s,v in sorted(sku_totals.items(),key=lambda x:x[1],reverse=True))+"。产品销售金额来自开放演示月度订单汇总表。"),
      ("库存快照与安全库存预警（2026-08-26）","；".join(inv_lines)+"。当前所有SKU均未低于安全库存。可用库存=期初+入库-出库，演示数据允许因盘点调整产生差异。"),
      ("客户分布与隐私说明", "开放样例客户共10家，全部使用客户甲至客户癸的匿名别名。区域分布：华东3家、华南3家、华北2家、西部2家。行业覆盖制造、零售、物流、专业服务、教育、能源和软件服务。数据库不包含姓名、电话、邮箱、地址、证件号或真实合同。"),
      ("客户服务SLA与满意度",f"2026年8月服务工单{svc[1]}件，已解决{svc[2]}件，解决率{pct(svc[2],svc[1])}%，平均首次响应{svc[3]}分钟，满意度{svc[4]}%，SLA达标率{svc[5]}%。演示服务目标：首次响应不超过30分钟，SLA达标率不低于95%。"),
      ("开放数据库表结构与查询口径","开放表包括open_company_department部门、open_company_product产品、open_company_customer匿名客户、open_company_order_monthly月度订单汇总、open_company_inventory库存、open_company_finance_monthly财务月报、open_company_service_monthly服务月报。收入使用已确认演示订单金额；毛利=收入-成本；库存按快照日期；客户仅提供匿名聚合信息。"),
      ("问答范围与使用示例","可提问：公司主营业务是什么、员工和部门有多少、有哪些产品及报价、2026年8月收入和毛利、1至8月区域销售排名、哪个产品收入最高、库存是否预警、客户行业分布、服务SLA如何。回答必须注明数据为虚构演示数据，不得推断真实个人或企业信息。"),
    ]
    return docs

conn=pymysql.connect(**DB)
try:
    with conn.cursor() as cur:
        for sql in SCHEMA: cur.execute(sql)
        for table in ["open_company_department","open_company_product","open_company_customer","open_company_order_monthly","open_company_inventory","open_company_finance_monthly","open_company_service_monthly"]:
            cur.execute(f"DELETE FROM {table}")
        cur.executemany("INSERT INTO open_company_department VALUES (%s,%s,%s,%s,%s,%s)",departments)
        cur.executemany("INSERT INTO open_company_product VALUES (%s,%s,%s,%s,%s,%s,%s)",products)
        cur.executemany("INSERT INTO open_company_customer VALUES (%s,%s,%s,%s,%s,%s)",customers)
        cur.executemany("INSERT INTO open_company_order_monthly VALUES (%s,%s,%s,%s,%s,%s,%s)",order_rows)
        cur.executemany("INSERT INTO open_company_inventory VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",inventory)
        cur.executemany("INSERT INTO open_company_finance_monthly VALUES (%s,%s,%s,%s,%s,%s)",finance_rows)
        cur.executemany("INSERT INTO open_company_service_monthly VALUES (%s,%s,%s,%s,%s,%s)",service)
        cur.execute("DELETE FROM kb_document WHERE title LIKE '公司概况与开放数据声明%' OR title IN ("+",".join(["%s"]*11)+")", tuple(x[0] for x in build_docs()[1:]))
        docs=build_docs()
        cur.executemany("INSERT INTO kb_document(title,content) VALUES(%s,%s)",docs)
        counts={}
        for table in ["open_company_department","open_company_product","open_company_customer","open_company_order_monthly","open_company_inventory","open_company_finance_monthly","open_company_service_monthly","kb_document"]:
            cur.execute(f"SELECT COUNT(*) c FROM {table}"); counts[table]=cur.fetchone()["c"]
    conn.commit()
    print(json.dumps({"status":"ok","company":COMPANY,"tables":counts,"knowledge_docs_added":len(build_docs()),"disclaimer":DISCLAIMER},ensure_ascii=False))
except Exception:
    conn.rollback(); raise
finally:
    conn.close()
