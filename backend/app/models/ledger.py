from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy import JSON as SAJSON
from sqlmodel import Field, SQLModel


class FaultCode(SQLModel, table=True):
    fault_code: str = Field(primary_key=True)
    fault_name: str
    possible_causes: str
    solution: str


class GridScaleProject(SQLModel, table=True):
    project_name: str = Field(primary_key=True)
    cod: str
    capacity_mwh: float
    cell_version: str
    pcs_model: str
    progress_status: str
    photo_paths: List[str] = Field(default_factory=list, sa_column=Column(SAJSON))


class CiDealerDelivery(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    region: str
    dealer_name: str = Field(index=True, unique=True)
    delivered_100c: int
    delivered_250: int


class WarehouseInventory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    warehouse_name: str = Field(index=True)
    product_model: str = Field(index=True)
    product_name: str
    category: str
    quantity: int
    unit: str = "pcs"


class WarehouseTransaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tx_no: str = Field(index=True, unique=True)
    warehouse_name: str = Field(index=True)
    tx_type: str
    product_model: str
    product_name: str
    quantity: int
    related_project: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WarehouseInventoryItem(SQLModel, table=True):
    item_no: str = Field(primary_key=True)
    description_zh: str
    specification: str
    total_quantity: int = 0
    damaged_quantity: int = 0
    available_quantity: int = 0
    photo_paths: List[str] = Field(default_factory=list, sa_column=Column(SAJSON))
    remarks: Optional[str] = None


FAULT_CODE_SEED = [
    FaultCode(
        fault_code="E024",
        fault_name="Battery Over Temperature / 电池过温",
        possible_causes="1) Ambient temperature too high. 2) Cooling fan or HVAC failure. 3) Battery pack thermal runaway risk. 4) Temperature sensor abnormal.",
        solution="1) Reduce ambient temperature and check ventilation. 2) Verify cooling fan, air duct, and HVAC status. 3) Inspect battery module temperature and alarm history. 4) If the fault persists, isolate the pack and contact service support.",
    ),
    FaultCode(
        fault_code="E031",
        fault_name="Communication Lost / 通信断开",
        possible_causes="1) Loose CAN/RS485/Ethernet cable. 2) Master-slave address mismatch. 3) Gateway offline. 4) EMC interference or damaged connector.",
        solution="1) Re-seat communication cables and check indicators. 2) Confirm address and baud-rate settings are consistent. 3) Restart the gateway or controller. 4) Replace damaged cables and re-test communication.",
    ),
    FaultCode(
        fault_code="E045",
        fault_name="Inverter Fault / 逆变器故障",
        possible_causes="1) Grid voltage out of range. 2) Internal inverter protection triggered. 3) Output relay abnormal. 4) Control board communication error.",
        solution="1) Measure grid voltage and frequency. 2) Check inverter alarm log and protection state. 3) Power-cycle the unit after confirming safety. 4) Escalate for module-level inspection if the alarm repeats.",
    ),
    FaultCode(
        fault_code="E052",
        fault_name="Battery Cell Voltage Imbalance / 电芯压差过大",
        possible_causes="1) Long-term SOC inconsistency. 2) Cell aging. 3) BMS sampling abnormal. 4) Improper balancing process.",
        solution="1) Run a full charge-balancing cycle according to the maintenance procedure. 2) Compare cell voltages and identify abnormal modules. 3) Verify BMS sampling harness and connectors. 4) Replace degraded cells or module assemblies when required.",
    ),
    FaultCode(
        fault_code="E067",
        fault_name="Insulation Resistance Low / 绝缘电阻低",
        possible_causes="1) Moisture ingress. 2) DC cable insulation damaged. 3) Connector contamination. 4) External ground fault.",
        solution="1) Stop operation and perform insulation test. 2) Dry the cabinet and verify sealing. 3) Inspect all DC cables and connectors. 4) Remove external ground faults before restart.",
    ),
    FaultCode(
        fault_code="E073",
        fault_name="BMS Power Supply Abnormal / BMS供电异常",
        possible_causes="1) Auxiliary power supply unstable. 2) Fuse blown. 3) Loose power harness. 4) BMS board failure.",
        solution="1) Check auxiliary power output and fuse status. 2) Tighten the power harness and terminal blocks. 3) Measure the BMS supply voltage under load. 4) Replace the BMS board if the voltage is still abnormal.",
    ),
]


GRID_SCALE_PROJECT_SEED = [
    GridScaleProject(
        project_name="418 项目",
        cod="2025-11-18",
        capacity_mwh=418.0,
        cell_version="LFP-314Ah V2",
        pcs_model="PCS-2500H",
        progress_status="正式并网",
        photo_paths=["/assets/projects/418-01.jpg", "/assets/projects/418-02.jpg", "/assets/projects/418-03.jpg", "/assets/projects/418-04.jpg"],
    ),
    GridScaleProject(
        project_name="Dune Horizon Project",
        cod="2025-08-03",
        capacity_mwh=240.0,
        cell_version="LFP-280Ah V1",
        pcs_model="PCS-2000H",
        progress_status="调试中",
        photo_paths=["/assets/projects/dune-01.jpg", "/assets/projects/dune-02.jpg", "/assets/projects/dune-03.jpg"],
    ),
    GridScaleProject(
        project_name="North Bay Storage",
        cod="2025-09-12",
        capacity_mwh=120.0,
        cell_version="LFP-314Ah V1",
        pcs_model="PCS-1250H",
        progress_status="土建施工",
        photo_paths=["/assets/projects/northbay-01.jpg", "/assets/projects/northbay-02.jpg"],
    ),
    GridScaleProject(
        project_name="Sahara Export Hub",
        cod="2025-06-27",
        capacity_mwh=75.0,
        cell_version="LFP-280Ah V1",
        pcs_model="PCS-1000H",
        progress_status="设备上岸",
        photo_paths=["/assets/projects/sahara-01.jpg", "/assets/projects/sahara-02.jpg", "/assets/projects/sahara-03.jpg"],
    ),
    GridScaleProject(
        project_name="Baltic Port ESS",
        cod="2025-05-15",
        capacity_mwh=60.0,
        cell_version="LFP-280Ah V1",
        pcs_model="PCS-1250H",
        progress_status="清关中",
        photo_paths=["/assets/projects/baltic-01.jpg"],
    ),
]


CI_DELIVERY_SEED = [
    CiDealerDelivery(region="Germany", dealer_name="Munich Energy Partners", delivered_100c=128, delivered_250=64),
    CiDealerDelivery(region="Netherlands", dealer_name="Rotterdam Solar Hub", delivered_100c=92, delivered_250=41),
    CiDealerDelivery(region="Poland", dealer_name="Warsaw Green Power", delivered_100c=75, delivered_250=38),
    CiDealerDelivery(region="Spain", dealer_name="Madrid Industrial Energy", delivered_100c=146, delivered_250=82),
    CiDealerDelivery(region="South Africa", dealer_name="Cape Storage Alliance", delivered_100c=61, delivered_250=27),
    CiDealerDelivery(region="UAE", dealer_name="Dubai Channel Partner", delivered_100c=110, delivered_250=55),
]


WAREHOUSE_INVENTORY_SEED = [
    WarehouseInventory(warehouse_name="europe", product_model="100C", product_name="100C 储能柜", category="柜体", quantity=42),
    WarehouseInventory(warehouse_name="europe", product_model="250", product_name="250 储能柜", category="柜体", quantity=28),
    WarehouseInventory(warehouse_name="europe", product_model="PCS", product_name="PCS 主机", category="核心配件", quantity=11),
    WarehouseInventory(warehouse_name="europe", product_model="BMS", product_name="BMS 主控板", category="核心配件", quantity=37),
    WarehouseInventory(warehouse_name="europe", product_model="CableKit", product_name="线缆包", category="核心配件", quantity=120),
    WarehouseInventory(warehouse_name="north_america", product_model="100C", product_name="100C 储能柜", category="柜体", quantity=31),
    WarehouseInventory(warehouse_name="north_america", product_model="250", product_name="250 储能柜", category="柜体", quantity=19),
    WarehouseInventory(warehouse_name="north_america", product_model="PCS", product_name="PCS 主机", category="核心配件", quantity=8),
    WarehouseInventory(warehouse_name="north_america", product_model="BMS", product_name="BMS 主控板", category="核心配件", quantity=26),
    WarehouseInventory(warehouse_name="north_america", product_model="CableKit", product_name="线缆包", category="核心配件", quantity=74),
]


WAREHOUSE_TRANSACTION_SEED = [
    WarehouseTransaction(
        tx_no="WH-EU-0001",
        warehouse_name="europe",
        tx_type="国内到货入库",
        product_model="100C",
        product_name="100C 储能柜",
        quantity=8,
        related_project="418 项目",
    ),
    WarehouseTransaction(
        tx_no="WH-EU-0002",
        warehouse_name="europe",
        tx_type="现场客诉领用出库",
        product_model="CableKit",
        product_name="线缆包",
        quantity=5,
        related_project="Baltic Port ESS",
    ),
    WarehouseTransaction(
        tx_no="WH-NA-0001",
        warehouse_name="north_america",
        tx_type="国内到货入库",
        product_model="250",
        product_name="250 储能柜",
        quantity=4,
        related_project="North Bay Storage",
    ),
]


WAREHOUSE_INVENTORY_ITEM_SEED_DATA = [
    {"item_no": "01240500033", "description_zh": "PCS-2000G2/215kW储能变流器整机TUV版-不带包材-批产-常熟方案 PCS", "specification": "JS215SB-TUV", "total_quantity": 12, "damaged_quantity": 2, "available_quantity": 10, "photo_paths": [], "remarks": ""},
    {"item_no": "01161500015", "description_zh": "水冷机组/8kw-CE认证版 Water-cooled unit", "specification": "LCI-80CR-10A3R1SZ3-1227C", "total_quantity": 5, "damaged_quantity": 1, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01161100061", "description_zh": "1xRJ45以太网输入+1xRJ45带电源输出以太网 1xRJ45 Enthernet input+1xRJ45 Enthernet output power with power suppl", "specification": "UL9000-SWIN3H-D", "total_quantity": 1, "damaged_quantity": 0, "available_quantity": 1, "photo_paths": [], "remarks": ""},
    {"item_no": "01130500431", "description_zh": "以太网远程控制器（16DI,16继电器输出,1路RS232,1路RS485） Enthernet Remoter Controller", "specification": "CX-5216E-QD", "total_quantity": 1, "damaged_quantity": 0, "available_quantity": 1, "photo_paths": [], "remarks": ""},
    {"item_no": "01160800038", "description_zh": "1个百兆以太网电口/8路RS232或RS485串口联网直流电源DC9~36V输入 1 Fast Enthernet Prot/8 RS232orRS485 Serial Ports for Networking DC Power Supply DC9-36", "specification": "MPORT3108 /具有防反接保护", "total_quantity": 1, "damaged_quantity": 0, "available_quantity": 1, "photo_paths": [], "remarks": ""},
    {"item_no": "01161200003", "description_zh": "交换机/DC9~60V/2层管理型/4个千兆SFP光口/8个自适应以太网接口 Switch", "specification": "MISCOM7212G-4GF-8GT", "total_quantity": 1, "damaged_quantity": 0, "available_quantity": 1, "photo_paths": [], "remarks": ""},
    {"item_no": "01160800641", "description_zh": "隔离型CAN转以太网服务器,电源DC9~36V,壁挂式 Isolated CAN-to-Ethernet Server", "specification": "MW-CANET200,壁挂式", "total_quantity": 1, "damaged_quantity": 0, "available_quantity": 1, "photo_paths": [], "remarks": ""},
    {"item_no": "01160900003", "description_zh": "欧标气溶胶，100g，温度启动 Aperosol 100g", "specification": "100T", "total_quantity": 3, "damaged_quantity": 0, "available_quantity": 3, "photo_paths": [], "remarks": ""},
    {"item_no": "01161100016", "description_zh": "电源模块/85 - 264VAC输入/输出24V/52.8W/4000VAC隔离 Power Module", "specification": "LRS-50-24", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01161100011", "description_zh": "开关电源/100W/24V输出 Switching power supply/100W/24V Output", "specification": "LM100-23B24", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01161100012", "description_zh": "开关电源/350W/24V输出 Switching Power Supply/350W/24V Output", "specification": "LM350-10B24", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01161100013", "description_zh": "开关电源/150W/24V输出 Switching Power Supply/150W/24V Output", "specification": "LM150-23B24", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01161100020", "description_zh": "开关电源/50W/12V输出/欧标导轨安装方式 Switching Power Supply/50W/12V Output/DIN Rail Mounting", "specification": "LI50-20B12PU", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01161100021", "description_zh": "开关电源/100W/24V输出/欧标导轨安装方式 Switching Power Supply/100W/24V Output/DIN Rail Mounting", "specification": "LI100-20B24PR2", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01161100022", "description_zh": "开关电源/240W/24V输出/金属欧标导轨安装方式 Switching Power Supply/240W/24V Output/DIN Rail Mounting", "specification": "LIF240-10B24R2", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01161100023", "description_zh": "DC/DC电源模块/DC100-1000V输入/DC24V输出/200W/导轨型 DC/DC Converter/DC100-1000V Input/DC24V Output/200W/DIN Rail Mounting", "specification": "PV200-29B24R2", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01161100024", "description_zh": "DC/DC电源模块/DC100-1000V输入/DC12V输出/120W/导轨型 DC/DC Converter/DC100-1000V Input/DC12V Output/120W/DIN Rail Mounting", "specification": "PV120-08B12P-R2", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01130300051", "description_zh": "重载连接器插芯/10Pin公针+10Pin母针 Heavy-duty Connector Core/10Pin Male + 10Pin Female", "specification": "HE-010-M + HE-010-F", "total_quantity": 4, "damaged_quantity": 0, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01130300052", "description_zh": "重载连接器外壳/双扣侧出线/M20 Heavy-duty Connector Housing/Double-lock Side Outlet/M20", "specification": "H10B-SE-2B-M20", "total_quantity": 4, "damaged_quantity": 0, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01130300053", "description_zh": "重载连接器底座/双扣开孔底座 Heavy-duty Connector Base/Double-lock Panel Mount Base", "specification": "H10B-AG-2B", "total_quantity": 4, "damaged_quantity": 0, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01130300054", "description_zh": "重载连接器接头/防水金属电缆固定头/M20 Heavy-duty Connector Gland/Waterproof Metal Cable Gland/M20", "specification": "M20x1.5", "total_quantity": 4, "damaged_quantity": 0, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01130500118", "description_zh": "浪涌保护器/千兆以太网信号防雷器 Surge Protective Device/Gigabit Ethernet Signal Lightning Arrester", "specification": "SPD-RJ45-1000M", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01130500119", "description_zh": "浪涌保护器/RS485信号防雷器 Surge Protective Device/RS485 Signal Lightning Arrester", "specification": "SPD-485-24V", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01161000001", "description_zh": "温湿度传感器/DC9~36V/RS485输出 Temperature and Humidity Sensor/DC9~36V/RS485 Output", "specification": "TH-RS485-S", "total_quantity": 3, "damaged_quantity": 0, "available_quantity": 3, "photo_paths": [], "remarks": ""},
    {"item_no": "01161000002", "description_zh": "浸水传感器/DC9~36V/继电器输出 Water Immersion Sensor/DC9~36V/Relay Output", "specification": "WI-RELAY-S", "total_quantity": 3, "damaged_quantity": 0, "available_quantity": 3, "photo_paths": [], "remarks": ""},
    {"item_no": "01161000003", "description_zh": "烟雾传感器/DC9~36V/继电器输出 Smoke Sensor/DC9~36V/Relay Output", "specification": "SM-RELAY-S", "total_quantity": 3, "damaged_quantity": 0, "available_quantity": 3, "photo_paths": [], "remarks": ""},
    {"item_no": "01161000004", "description_zh": "门禁传感器/行程开关式 Door Access Sensor/Limit Switch Type", "specification": "DS-LIMIT-S", "total_quantity": 4, "damaged_quantity": 0, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01130100010", "description_zh": "微型断路器/1P/C10A/MCB Miniature Circuit Breaker/1P/C10A", "specification": "iC65N 1P C10A", "total_quantity": 5, "damaged_quantity": 0, "available_quantity": 5, "photo_paths": [], "remarks": ""},
    {"item_no": "01130100011", "description_zh": "微型断路器/2P/C16A/MCB Miniature Circuit Breaker/2P/C16A", "specification": "iC65N 2P C16A", "total_quantity": 5, "damaged_quantity": 0, "available_quantity": 5, "photo_paths": [], "remarks": ""},
    {"item_no": "01130100012", "description_zh": "微型断路器/3P/C32A/MCB Miniature Circuit Breaker/3P/C32A", "specification": "iC65N 3P C32A", "total_quantity": 3, "damaged_quantity": 0, "available_quantity": 3, "photo_paths": [], "remarks": ""},
    {"item_no": "01130100020", "description_zh": "塑壳断路器/3P/250A/MCCB Molded Case Circuit Breaker/3P/250A", "specification": "NSX250F 3P 250A", "total_quantity": 1, "damaged_quantity": 0, "available_quantity": 1, "photo_paths": [], "remarks": ""},
    {"item_no": "01130200001", "description_zh": "交流接触器/3P/25A/线圈24VDC AC Contactor/3P/25A/Coil 24VDC", "specification": "LC1D25BD", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01130200002", "description_zh": "交流接触器/3P/40A/线圈24VDC AC Contactor/3P/40A/Coil 24VDC", "specification": "LC1D40ABD", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01130200010", "description_zh": "中间继电器/2对触点/24VDC线圈/带底座 Intermediate Relay/2PDT/24VDC Coil/with Socket", "specification": "RXM2LB2BD + RXZE2M114M", "total_quantity": 5, "damaged_quantity": 0, "available_quantity": 5, "photo_paths": [], "remarks": ""},
    {"item_no": "01130200011", "description_zh": "中间继电器/4对触点/24VDC线圈/带底座 Intermediate Relay/4PDT/24VDC Coil/with Socket", "specification": "RXM4LB2BD + RXZE2M114M", "total_quantity": 5, "damaged_quantity": 0, "available_quantity": 5, "photo_paths": [], "remarks": ""},
    {"item_no": "01130400001", "description_zh": "熔断器/10x38/直流1000V/15A Fuse/10x38/1000VDC/15A", "specification": "gPV 10x38 15A 1000VDC", "total_quantity": 20, "damaged_quantity": 0, "available_quantity": 20, "photo_paths": [], "remarks": ""},
    {"item_no": "01130400002", "description_zh": "熔断器底座/10x38/光伏专用 Fuse Holder/10x38/PV Special", "specification": "PV-1038-1P", "total_quantity": 10, "damaged_quantity": 0, "available_quantity": 10, "photo_paths": [], "remarks": ""},
    {"item_no": "01130400010", "description_zh": "快速熔断器/aR 700V/200A Fast-acting Fuse/aR 700V/200A", "specification": "FWH-200A", "total_quantity": 4, "damaged_quantity": 0, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01130400011", "description_zh": "快速熔断器/aR 1000V/400A Fast-acting Fuse/aR 1000V/400A", "specification": "170M3019 (400A 1000V)", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01160100001", "description_zh": "BMS主控单元/三级架构主控模块 BMS Master Control Unit/3-Level Architecture Master Module", "specification": "BMS-MU-1000V", "total_quantity": 1, "damaged_quantity": 0, "available_quantity": 1, "photo_paths": [], "remarks": ""},
    {"item_no": "01160100002", "description_zh": "BMS从控单元/采卡/16串采样 BMS Slave Control Unit/CSC/16S Sampling", "specification": "BMS-SU-16S", "total_quantity": 4, "damaged_quantity": 0, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01160100003", "description_zh": "高压箱控制板/HVCU High Voltage Control Unit/HVCU", "specification": "HVCU-1000V-A", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01160200001", "description_zh": "Hall电流传感器/±500A/DC±15V供电/输出4-20mA Hall Current Sensor/±500A/DC±15V/4-20mA Output", "specification": "HAS 500-S", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01160200002", "description_zh": "Hall电流传感器/±1000A/DC±15V供电 Hall Current Sensor/±1000A/DC±15V", "specification": "HAS 1000-S", "total_quantity": 1, "damaged_quantity": 0, "available_quantity": 1, "photo_paths": [], "remarks": ""},
    {"item_no": "01160300001", "description_zh": "绝缘监测仪/1000VDC/RS485 Insulation Monitoring Device/1000VDC/RS485", "specification": "IMD1000-RS485", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01160400001", "description_zh": "风扇/DC24V/120x120x38mm/轴流风扇 DC Fan/DC24V/120x120x38mm/Axial Fan", "specification": "4414/2HH", "total_quantity": 6, "damaged_quantity": 0, "available_quantity": 6, "photo_paths": [], "remarks": ""},
    {"item_no": "01160400002", "description_zh": "离心风扇/AC230V/225mm Centrifugal Fan/AC230V/225mm", "specification": "R2E225-RA92-09", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01160500001", "description_zh": "水冷液/乙二醇基/-35℃防冻/20L桶装 Coolant/Ethylene Glycol-based/-35℃ Antifreeze/20L Drum", "specification": "EC-35-20L", "total_quantity": 4, "damaged_quantity": 0, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01160500002", "description_zh": "液冷快速插拔接头/公头/DN12 Quick-disconnect Coupling/Male/DN12", "specification": "QC-DN12-M", "total_quantity": 8, "damaged_quantity": 0, "available_quantity": 8, "photo_paths": [], "remarks": ""},
    {"item_no": "01160500003", "description_zh": "液冷快速插拔接头/母头/DN12 Quick-disconnect Coupling/Female/DN12", "specification": "QC-DN12-F", "total_quantity": 8, "damaged_quantity": 0, "available_quantity": 8, "photo_paths": [], "remarks": ""},
    {"item_no": "01160600001", "description_zh": "防爆阀/M12/IP68 Pressure Relief Valve/M12/IP68", "specification": "PRV-M12-IP68", "total_quantity": 10, "damaged_quantity": 0, "available_quantity": 10, "photo_paths": [], "remarks": ""},
    {"item_no": "01160600002", "description_zh": "透气阀/M12/IP68 Breathable Valve/M12/IP68", "specification": "BV-M12-IP68", "total_quantity": 10, "damaged_quantity": 0, "available_quantity": 10, "photo_paths": [], "remarks": ""},
    {"item_no": "01160700001", "description_zh": "五孔插座+开关模组/欧标导轨安装 European Standard Socket+Switch Module/DIN Rail", "specification": "SD-EU-240", "total_quantity": 3, "damaged_quantity": 0, "available_quantity": 3, "photo_paths": [], "remarks": ""},
    {"item_no": "01160700002", "description_zh": "LED柜内照明灯/AC220V/5W/带磁吸功能 LED Cabinet Light/AC220V/5W/Magnetic", "specification": "LED-CL-5W", "total_quantity": 4, "damaged_quantity": 0, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01130600001", "description_zh": "端子排/2.5平方/接线端子/灰色 Terminal Block/2.5mm²/Grey", "specification": "UK-2.5B", "total_quantity": 100, "damaged_quantity": 0, "available_quantity": 100, "photo_paths": [], "remarks": ""},
    {"item_no": "01130600002", "description_zh": "端子排/4平方/接地端子/黄绿双色 Terminal Block/4mm²/PE/Yellow-Green", "specification": "USLKG-4", "total_quantity": 20, "damaged_quantity": 0, "available_quantity": 20, "photo_paths": [], "remarks": ""},
    {"item_no": "01130600003", "description_zh": "端子排挡板/UK-2.5B专用 Terminal Block End Cover/for UK-2.5B", "specification": "D-UK-2.5B", "total_quantity": 20, "damaged_quantity": 0, "available_quantity": 20, "photo_paths": [], "remarks": ""},
    {"item_no": "01130600004", "description_zh": "端子固定件/导轨固定器 Terminal Block End Clamp/DIN Rail Mounting", "specification": "E/UK", "total_quantity": 20, "damaged_quantity": 0, "available_quantity": 20, "photo_paths": [], "remarks": ""},
    {"item_no": "01130700001", "description_zh": "网线/超六线CAT6A/屏蔽双绞线/1米 Patch Cord/CAT6A/SFTP/1m", "specification": "CAT6A-SFTP-1M", "total_quantity": 10, "damaged_quantity": 0, "available_quantity": 10, "photo_paths": [], "remarks": ""},
    {"item_no": "01130700002", "description_zh": "网线/超六线CAT6A/屏蔽双绞线/3米 Patch Cord/CAT6A/SFTP/3m", "specification": "CAT6A-SFTP-3M", "total_quantity": 10, "damaged_quantity": 0, "available_quantity": 10, "photo_paths": [], "remarks": ""},
    {"item_no": "01130700010", "description_zh": "CAN通讯线/双绞屏蔽线/120欧姆终端电阻匹配 CAN Cable/STP/120 Ohm Matched", "specification": "CAN-STP-2x0.75", "total_quantity": 5, "damaged_quantity": 0, "available_quantity": 5, "photo_paths": [], "remarks": ""},
    {"item_no": "01130800001", "description_zh": "软铜排/铜软连接/250A规格 Flexible Copper Busbar/250A Specification", "specification": "FCB-250A-200MM", "total_quantity": 6, "damaged_quantity": 0, "available_quantity": 6, "photo_paths": [], "remarks": ""},
    {"item_no": "01130800002", "description_zh": "软铜排/铜软连接/500A规格 Flexible Copper Busbar/500A Specification", "specification": "FCB-500A-300MM", "total_quantity": 4, "damaged_quantity": 0, "available_quantity": 4, "photo_paths": [], "remarks": ""},
    {"item_no": "01161600001", "description_zh": "调试串口线/USB转RS485/带隔离 Debug Cable/USB to RS485/Isolated", "specification": "UT-890A", "total_quantity": 2, "damaged_quantity": 0, "available_quantity": 2, "photo_paths": [], "remarks": ""},
    {"item_no": "01161600002", "description_zh": "调试CAN卡/USB转CAN分析仪/双通道 Debug CAN Card/USB-to-CAN Analyzer/Dual Channel", "specification": "USBCAN-II-C", "total_quantity": 1, "damaged_quantity": 0, "available_quantity": 1, "photo_paths": [], "remarks": ""},
]

WAREHOUSE_INVENTORY_ITEM_SEED = [WarehouseInventoryItem(**item) for item in WAREHOUSE_INVENTORY_ITEM_SEED_DATA]
