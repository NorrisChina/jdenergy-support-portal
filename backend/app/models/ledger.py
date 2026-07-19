from __future__ import annotations

from datetime import datetime
from typing import Optional

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
    photo_paths: list[str] = Field(default_factory=list, sa_column=Column(SAJSON))


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
