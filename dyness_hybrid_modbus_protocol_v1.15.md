# Dyness Hybrid Inverter – Modbus RTU Protocol (LLM-readable Markdown)

- **Source document:** `Modbus_Protocol_Hybrid_S-V1_15.pdf` ("DYNESS Modbus Protocol – Hybrid Inverter", Firmware Team), latest revision **V1.15 (2026-07-08)**
- **Scope:** Modbus RTU register map for Dyness (DS) energy storage / hybrid inverters, accessed through the inverter's EMS (RS485) port.
- **Conversion notes (added by the converter, not part of the original):**
  - All register addresses are **decimal** (leading zeros in the source, e.g. `00003`, are only padding).
  - Scaling: `real value = raw value / Mult`. Example: `Vpv1` raw `2305` with Mult 10 means 230.5 V.
  - `Regs` = number of 16-bit Modbus registers occupied. Where the source gave only a single number in the Mult/Regs area, it is shown under `Regs` with `–` under `Mult`.
  - `R0` in the source is a typo for `RO` (read-only); it is normalised to `RO` here.
  - Chinese text in the source (change log, Table 8-24) is translated to English.
  - Places where the PDF text extraction was ambiguous are marked **[AMBIGUOUS]**; verify against the PDF.

---

## 1. Protocol description

| Item | Value |
|---|---|
| Protocol | Standard Modbus RTU (only for DS energy storage inverters) |
| Inverter (slave) address | 01H–F7H (1–247); factory default 01H |
| Default baud rate | 19200 bps |
| Byte format | 1 start bit, 8 data bits, 1 stop bit (10 bits total); D0 is the LSB, D7 the MSB |
| CRC | CRC16 (see section 7) |

### Function codes

| Code | Meaning |
|---|---|
| 03H | Read registers |
| 06H | Write single register |
| 10H | Write multiple registers |

### Error (exception) codes returned by the inverter

| Code | Meaning |
|---|---|
| 02H | Register address fault, or too many registers requested |
| 03H | Data error |
| 04H | Built-in verification code error |
| 05H | Communication time-out |

### Data types

| Type | Registers | Bytes | Description |
|---|---|---|---|
| Byte | 1 | 1 | |
| Integer (U16/S16) | 1 | 2 | Returned at once, high byte first |
| Long integer (U32/S32) / Float | 2 | 4 | Returned in two parts, high part first |
| STR | n | 2n | ASCII string |

---

## 2. Data frame format

All multi-byte fields are big-endian except the CRC, which is sent **low byte first**.

### 2.1 Read registers (function 03H)

**Request from host**

| # | Field | Example | Notes |
|---|---|---|---|
| 1 | Inverter address | 01H | 01H–F7H |
| 2 | Function code | 03H | |
| 3 | First register address, high byte | 00H | Example start address 0001H |
| 4 | First register address, low byte | 01H | |
| 5 | Register count, high byte | 00H | Example count 0002H |
| 6 | Register count, low byte | 02H | |
| 7 | CRC16 low byte | 95H | |
| 8 | CRC16 high byte | CBH | |

Example frame: `01 03 00 01 00 02 95 CB`

**Normal response from inverter**

| # | Field | Notes |
|---|---|---|
| 1 | Inverter address | 1–247 |
| 2 | Function code | 03H |
| 3 | Byte count (2N) | N = number of registers |
| 4 | Register 1 high byte | |
| 5 | Register 1 low byte | |
| … | … | |
| 2N+2 | Register N high byte | |
| 2N+3 | Register N low byte | |
| 2N+4 | CRC16 low byte | |
| 2N+5 | CRC16 high byte | |

**Error response (wrong register address or count):** `addr, 83H, 02H, CRC_lo, CRC_hi`

### 2.2 Write multiple registers (function 10H)

**Request from host**

| # | Field | Example |
|---|---|---|
| 1 | Inverter address | 01H |
| 2 | Function code | 10H |
| 3–4 | Start register address (hi, lo) | 0000H |
| 5–6 | Number of registers (hi, lo) | 0001H |
| 7 | Byte count N | 02H |
| 8–9 | Data (hi, lo) | 0AF0H |
| 10 | CRC16 low | A0H |
| 11 | CRC16 high | B4H |

**Normal response:** `01 10 00 00 00 01 01 C9`  (address, 10H, start address, register count, CRC low = 01H, CRC high = C9H)

**Error responses**
- Data faulty: `addr, 90H, 03H, CRC_lo, CRC_hi`
- Address or register count faulty: `addr, 90H, 02H, CRC_lo, CRC_hi`

### 2.3 Write single register (function 06H)

**Request from host**

| # | Field | Example |
|---|---|---|
| 1 | Device address | 01H |
| 2 | Function code | 06H |
| 3–4 | Register address (hi, lo) | 0000H |
| 5–6 | Data (hi, lo) | 0AF0H |
| 7–8 | CRC16 | 8FH, 2EH (as printed in the source) |

**Normal response:** echo of the request (same 8 bytes).

---

## 3. System wiring

- The compatible device (EMS / data logger) connects to the inverter's **EMS port** over RS485 (RJ45 connector).
- The inverter must be powered by DC (PV/battery) or AC before it can communicate.
- To sniff the interaction log, connect a laptop in parallel with the compatible device using an RS485 cable and an RS485-to-RJ45 adapter.

---

## 4. Running data / info registers (read-only)

### 4.1 Device information registers

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 0 | Modbus protocol version | RO | U16 | N/A | 1 | 1 | |
| 1 | Rated power | RO | U16 | W | 1 | 1 | |
| 2 | AC output type | RO | U16 | N/A | 1 | 1 | 0 = single phase; 1 = three phase four wire; 2 = three phase three wire; 3 = two phase three wire |
| 3 | Serial number | RO | STR | N/A | 1 | 11 | ASCII, 21 bytes |
| 14 | Device type | RO | STR | N/A | 1 | 2 | ASCII, 4 bytes |
| 16 | DSP1 software version | RO | U16 | N/A | 1 | 1 | |
| 17 | DSP2 software version | RO | U16 | N/A | 1 | 1 | |
| 18 | DSP SVN version | RO | U16 | N/A | 1 | 1 | |
| 19 | ARM software version | RO | U16 | N/A | 1 | 1 | |
| 20 | ARM SVN version | RO | U16 | N/A | 1 | 1 | |
| 21 | DSP internal firmware ver. | RO | STR | N/A | 1 | 6 | Example `'010100'` |
| 27 | ARM internal firmware ver. | RO | STR | N/A | 1 | 6 | Example `'000100'` |
| 33 | Device hardware ver. | RO | U16 | N/A | 1 | 1 | |
| 34 | SafetyModuleVer | RO | U16 | N/A | 1 | 1 | |
| 35 | Manufacture | RO | STR | N/A | 1 | 8 | "Dyness" |
| 43 | Power Ratio | RO | U16 | N/A | 1 | 1 | Power coefficient: 1, 10, 100 or 1000 (see note below) |
| 44 | ARC software version | RO | U16 | N/A | 1 | 1 | |
| 45 | ARC SVN version | RO | U16 | N/A | 1 | 1 | |
| 46 | BOX software version | RO | U16 | N/A | 1 | 1 | |
| 47 | BOX SVN version | RO | U16 | N/A | 1 | 1 | |
| 48–50 | Reserved | | | | | | |
| 51 | BMS Version | RO | U16 | N/A | 1 | 1 | Bit15–9 = Year, Bit8–5 = Month, Bit4–0 = Day; version string Y.M.D (added in V1.15) |

> **Power Ratio note (from change log V1.11):** the grid/backup/load power registers 120, 125, 130, 133, 135, 137, 143, 149, 155, 157, 159, 161 were changed from S32 to S16, and the **actual power = register value × power coefficient register (Power Ratio, reg 43)**. The register table below still lists them as S32 with 2 registers. **[AMBIGUOUS]** Check the data type against your firmware version.

### 4.2 Running data registers

**RTC and PV inputs**

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 100 | RTC | RO | U16 | N/A | 1 | 1 | Hbyte = year, Lbyte = month (year 13–99, month 1–12) |
| 101 | RTC | RO | U16 | N/A | 1 | 1 | Hbyte = day, Lbyte = hour (1–31 / 0–23) |
| 102 | RTC | RO | U16 | N/A | 1 | 1 | Hbyte = minute, Lbyte = second (0–59 / 0–59) |
| 103 | Vpv1 | RO | U16 | V | 10 | 1 | PV1 voltage |
| 104 | Ipv1 | RO | U16 | A | 10 | 1 | PV1 current |
| 105 | Ppv1 | RO | U16 | W | 1 | 1 | PV1 power |
| 106 | Vpv2 | RO | U16 | V | 10 | 1 | PV2 voltage |
| 107 | Ipv2 | RO | U16 | A | 10 | 1 | PV2 current |
| 108 | Ppv2 | RO | U16 | W | 1 | 1 | PV2 power |
| 109 | Vpv3 | RO | U16 | V | 10 | 1 | PV3 voltage |
| 110 | Ipv3 | RO | U16 | A | 10 | 1 | PV3 current |
| 111 | Ppv3 | RO | U16 | W | 1 | 1 | PV3 power |
| 112 | Vpv4 | RO | U16 | V | 10 | 1 | PV4 voltage |
| 113 | Ipv4 | RO | U16 | A | 10 | 1 | PV4 current |
| 114 | Ppv4 | RO | U16 | W | 1 | 1 | PV4 power |
| 115 | PV Mode | RO | U16 | N/A | – | 1 | PV module work mode, Tables 8-3 and 8-4 |
| 116 | Reserved1 | RO | U16 | N/A | – | 1 | |

**Grid**

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 117 | Vgrid_R | RO | U16 | V | 10 | 1 | R phase grid voltage |
| 118 | Igrid_R | RO | U16 | A | 10 | 1 | R phase grid current |
| 119 | Fgrid_R | RO | U16 | Hz | 100 | 1 | R phase grid frequency |
| 120 | Pgrid_R | RO | S32 | W | 1 | 2 | R phase grid power |
| 122 | Vgrid_S | RO | U16 | V | 10 | 1 | S phase grid voltage |
| 123 | Igrid_S | RO | U16 | A | 10 | 1 | S phase grid current |
| 124 | Fgrid_S | RO | U16 | Hz | 100 | 1 | S phase grid frequency |
| 125 | Pgrid_S | RO | S32 | W | 1 | 2 | S phase grid power |
| 127 | Vgrid_T | RO | U16 | V | 10 | 1 | T phase grid voltage |
| 128 | Igrid_T | RO | U16 | A | 10 | 1 | T phase grid current |
| 129 | Fgrid_T | RO | U16 | Hz | 100 | 1 | T phase grid frequency |
| 130 | Pgrid_T | RO | S32 | W | 1 | 2 | T phase grid power |
| 132 | Grid Mode | RO | U16 | – | – | 1 | Grid mode, Table 8-10 |
| 133 | AC P Power | RO | S32 | W | 1 | 2 | AC active power |
| 135 | AC Q Power | RO | S32 | Var | 1 | 2 | AC reactive power |
| 137 | AC S Power | RO | U32 | VA | 1 | 2 | AC apparent power |

**Back-Up (EPS) output and load**

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 139 | Back-Up Vload_R | RO | U16 | V | 10 | 1 | R phase load voltage of Back-Up |
| 140 | Back-Up Iload_R | RO | U16 | A | 10 | 1 | R phase load current of Back-Up |
| 141 | Back-Up Fload_R | RO | U16 | Hz | 100 | 1 | R phase load frequency of Back-Up |
| 142 | Load Mode_R | RO | U16 | – | – | 1 | Load work mode, Table 8-11 |
| 143 | PBackUp_R | RO | S32 | W | 1 | 2 | R phase load power of Back-Up |
| 145 | Back-Up Vload_S | RO | U16 | V | 10 | 1 | S phase load voltage of Back-Up |
| 146 | Back-Up Iload_S | RO | U16 | A | 10 | 1 | S phase load current of Back-Up |
| 147 | Back-Up Fload_S | RO | U16 | Hz | 100 | 1 | S phase load frequency of Back-Up |
| 148 | Load Mode_S | RO | U16 | – | – | 1 | Load work mode, Table 8-11 |
| 149 | PBackUp_S | RO | S32 | W | 1 | 2 | S phase load power of Back-Up |
| 151 | Back-Up Vload_T | RO | U16 | V | 10 | 1 | T phase load voltage of Back-Up |
| 152 | Back-Up Iload_T | RO | U16 | A | 10 | 1 | T phase load current of Back-Up |
| 153 | Back-Up Fload_T | RO | U16 | Hz | 100 | 1 | T phase load frequency of Back-Up |
| 154 | Load Mode_T | RO | U16 | – | – | 1 | Load work mode, Table 8-11 |
| 155 | PBackUp_T | RO | S32 | W | 1 | 2 | T phase load power |
| 157 | PLoad_R | RO | S32 | W | 1 | 2 | R phase load power |
| 159 | PLoad_S | RO | S32 | W | 1 | 2 | S phase load power |
| 161 | PLoad_T | RO | S32 | W | 1 | 2 | T phase load power |
| 163 | Ups Load Percent | RO | U16 | % | 100 | 1 | |

**Temperatures, bus, battery 1, status**

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 164 | inter temperature | RO | S16 | °C | 10 | 1 | Inverter internal temperature |
| 165 | Radiator temperature | RO | S16 | °C | 10 | 1 | |
| 166 | module temperature | RO | S16 | °C | 10 | 1 | |
| 167 | FunctionBitValue | RO | U16 | – | – | 1 | |
| 168 | BUSVoltage | RO | U16 | V | 10 | 1 | BUS voltage |
| 169 | NBUSVoltage | RO | U16 | V | 10 | 1 | NBUS voltage |
| 170 | Vbattery1 | RO | U16 | V | 10 | 1 | First group battery voltage |
| 171 | Ibattery1 | RO | S16 | A | 10 | 1 | First group battery current |
| 172 | Pbattery1 | RO | S16 | W | 1 | 1 | First group battery power |
| 173 | Battery1 Mode | RO | U16 | – | – | 1 | 1st group battery work mode, Table 8-9 |
| 174 | Warning code | RO | U16 | – | – | 1 | Table 8-24 |
| 175 | SafetyCountry | RO | U16 | – | – | 1 | Table 8-21 |
| 176 | Work State | RO | U16 | – | – | 1 | Table 8-1 |
| 177 | Error Message_L | RO | U32 | – | – | 1 | Failure status, Table 8-2 (low word) |
| 178 | Error Message_H | RO | U32 | – | – | 1 | Failure status, Table 8-2 (high word) |
| 179 | Error Message Ex_L | RO | U32 | – | – | 1 | Failure status, Table 8-2 Ex (low word) |
| 180 | Error Message Ex_H | RO | U32 | – | – | 1 | Failure status, Table 8-2 Ex (high word) |

**Energy counters** (unit shown in source as "1KW.Hr", Mult 10 → 0.1 kWh resolution; `_L`/`_H` are low/high words of one U32)

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 181 | PV E-Total_L | RO | U32 | kWh | 10 | 1 | Total PV energy |
| 182 | PV E-Total_H | RO | U32 | kWh | 10 | 1 | Total PV energy |
| 183 | PV E-Day | RO | U16 | kWh | 10 | 1 | PV energy today |
| 184 | E-Total_L | RO | U32 | kWh | 10 | 1 | Total energy fed to grid |
| 185 | E-Total_H | RO | U32 | kWh | 10 | 1 | Total energy fed to grid |
| 186 | h-Total_L | RO | U32 | h | 1 | 1 | Total feeding hours |
| 187 | h-Total_H | RO | U32 | h | 1 | 1 | Total feeding hours |
| 188 | E-Day-Sell | RO | U16 | kWh | 10 | 1 | Energy fed to grid today |
| 189 | E-Total-Buy_L | RO | U32 | kWh | 10 | 1 | Total energy bought from grid |
| 190 | E-Total-Buy_H | RO | U32 | kWh | 10 | 1 | Total energy bought from grid |
| 191 | E-Day-Buy | RO | U16 | kWh | 10 | 1 | Energy bought from grid today |
| 192 | E-Total-Load_L | RO | U32 | kWh | 10 | 1 | Total load energy |
| 193 | E-Total-Load_H | RO | U32 | kWh | 10 | 1 | Total load energy |
| 194 | E-Load-Day | RO | U16 | kWh | 10 | 1 | Load energy today |
| 195 | E-BatteryCharge_L | RO | U32 | kWh | 10 | 1 | Total charge energy |
| 196 | E-BatteryCharge_H | RO | U32 | kWh | 10 | 1 | Total charge energy |
| 197 | E-Charge-Day | RO | U16 | kWh | 10 | 1 | Charge energy today |
| 198 | E-BatteryDischarge_L | RO | U32 | kWh | 10 | 1 | Total discharge energy |
| 199 | E-BatteryDischarge_H | RO | U32 | kWh | 10 | 1 | Total discharge energy |
| 200 | E-discharge-Day | RO | U16 | kWh | 10 | 1 | Discharge energy today |

**Diagnostics, battery control, operate mode**

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 201 | CPLD code | RO | U16 | N/A | 1 | 1 | Table 8-17 |
| 202 | DiagStatus_L | RO | U32 | N/A | 1 | 1 | Table 8-14 (low word) |
| 203 | DiagStatus_H | RO | U32 | N/A | 1 | 1 | Table 8-14 (high word) |
| 204 | DiagStatusEx_L | RO | U32 | N/A | 1 | 1 | Table 8-14 (low word) |
| 205 | DiagStatusEx_H | RO | U32 | N/A | 1 | 1 | Table 8-14 (high word) |
| 206 | wChargerCtrlFlg | RO | U16 | N/A | 1 | 1 | Info used by manufacturer |
| 207 | BattCtrlFlagBySafety | RO | U16 | N/A | 1 | 1 | Info used by manufacturer |
| 208 | BattPowerLmtBySafety_L | RO | S32 | W | 1 | 1 | Info used by manufacturer |
| 209 | BattPowerLmtBySafety_H | RO | S32 | W | 1 | 1 | Info used by manufacturer |
| 210 | BatteryCtrlMode | RO | U16 | N/A | 1 | 1 | Info used by manufacturer |
| 211 | BatteryCtrlPower_L | RO | U32 | W | 1 | 1 | Info used by manufacturer |
| 212 | BatteryCtrlPower_H | RO | U32 | W | 1 | 1 | Info used by manufacturer |
| 213 | BatterySOCValue | RO | U16 | % | 1 | 1 | SOC of battery 1 |
| 214 | Operate Mode | RO | U16 | N/A | 1 | 1 | 0 = self-use; 1 = off-grid; 2 = backup; 3 = TOU; 4 = export; 5 = import; 6 = battery priority; 7 = dynamic trade |
| 215–224 | SelfDefine10 … SelfDefine1 | RO | U16 | NA | NA | 1 each | Info used by manufacturer (215 = SelfDefine10, 216 = SelfDefine9, … 224 = SelfDefine1) |

**Running data extra**

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 250 | SafetyDetailedErrorMsg | RO | U64 | NA | 1 | 4 | |
| 254 | InvDetailedErrorMsg | RO | U64 | NA | 1 | 4 | |
| 258 | InvDetailedStatusMsg | RO | U64 | NA | 1 | 4 | |
| 262 | Vbattery2 | RO | U16 | V | 10 | 1 | Second group battery voltage |
| 263 | Ibattery2 | RO | S16 | A | 10 | 1 | Second group battery current |
| 264 | Pbattery2 | RO | S16 | W | 1 | 1 | Second group battery power |
| 265 | Battery2 Mode | RO | U16 | NA | 1 | 1 | 2nd group battery work mode, Table 8-9 |
| 266 | Vutility_R | RO | U16 | V | 10 | 1 | R phase utility voltage |
| 267 | Iutility_R | RO | U16 | A | 10 | 1 | R phase utility current |
| 268 | Putility_R | RO | S32 | W | 1 | 2 | R phase utility power |
| 270 | Vutility_S | RO | U16 | V | 10 | 1 | S phase utility voltage |
| 271 | Iutility_S | RO | U16 | A | 10 | 1 | S phase utility current |
| 272 | Putility_S | RO | S32 | W | 1 | 2 | S phase utility power |
| 274 | Vutility_T | RO | U16 | V | 10 | 1 | Source says "S phase" (copy-paste typo; it is T phase) |
| 275 | Iutility_T | RO | U16 | A | 10 | 1 | T phase utility current |
| 276 | Putility_T | RO | S32 | W | 1 | 2 | T phase utility power |
| 278 | Futility | RO | U16 | Hz | 100 | 1 | Utility frequency |
| 378 | PowerR_ACCouple | RO | U16 | W | 1 | 1 | |
| 379 | PowerS_ACCouple | RO | U16 | W | 1 | 1 | |
| 380 | PowerT_ACCouple | RO | U16 | W | 1 | 1 | |
| 385 | TotalWattUtility | RO | S32 | W | 1 | 2 | |
| 387 | TotalVarUtility | RO | S32 | Var | 1 | 2 | |
| 389 | TotalVAUtility | RO | S32 | VA | 1 | 2 | |

### 4.3 BMS information registers

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 2000 | DRMStatus | RO | U16 | – | – | 1 | Table 8-15 |
| 2001 | BattTypeIndex | RO | U16 | – | 1 | 1 | Battery manufacturer index setting |
| 2002 | BMS COMM Status | RO | U16 | – | 1 | 1 | 1 = OK, 0 = NG |
| 2003 | BMS Pack Temperature | RO | S16 | – | 10 | 1 | (S16 since V1.09) |
| 2004 | BMS Charge Imax | RO | U16 | – | – | 1 | |
| 2005 | BMS Discharge Imax | RO | U16 | – | – | 1 | |
| 2006 | BMS Error Code L | RO | U16 | – | – | 1 | Bits 0–15, Table 8-7 |
| 2007 | BMS Error Code H | RO | U16 | NA | NA | 1 | Bits 16–31, Table 8-7 |
| 2008 | BMS Warning Code L | RO | U16 | – | – | 1 | Bits 0–15, Table 8-8 |
| 2009 | BMS Warning Code H | RO | U16 | NA | NA | 1 | Bits 16–31, Table 8-8 |
| 2010 | SOC | RO | U16 | % | 1 | 1 | First group battery capacity |
| 2011 | BMS SOH | RO | U16 | % | 1 | 1 | |
| 2012 | BMS Battery strings | RO | U16 | Pcs | 1 | 1 | |
| 2013 | Battery protocol | RO | U16 | – | – | 1 | |
| 2014 | BMS Software Version | RO | U16 | NA | 1 | 1 | |
| 2015 | Battery Hardware Version | RO | U16 | NA | 1 | 1 | |
| 2016 | Maximum cell temperature ID | RO | U16 | NA | 1 | 1 | |
| 2017 | Minimum cell temperature ID | RO | U16 | NA | 1 | 1 | |
| 2018 | Maximum cell voltage ID | RO | U16 | NA | 1 | 1 | |
| 2019 | Minimum cell voltage ID | RO | U16 | NA | 1 | 1 | |
| 2020 | Maximum cell temperature | RO | U16 | °C | 10 | 1 | |
| 2021 | Minimum cell temperature | RO | U16 | °C | 10 | 1 | |
| 2022 | Maximum cell voltage | RO | U16 | mV | 1 | 1 | |
| 2023 | Minimum cell voltage | RO | U16 | mV | 1 | 1 | |
| 2024 | Battery Total Voltage | RO | U16 | V | 10 | 1 | |
| 2025 | Battery Current | RO | U16 | A | 10 | 1 | |
| 2026 | Cycle Times | RO | U16 | NA | NA | 1 | |
| 2027–2055 | Pass Infomation4 … Pass Infomation32 | RO | U16 | NA | NA | 1 each | Pass-through info; 2027 = Info4, 2028 = Info5, … 2055 = Info32 (29 registers) |

---

## 5. Setting / controlling registers (read/write)

Legend: RW = read/write, WO = write-only, RO/R = read-only. `N` in ranges = number of battery strings (reg 25351).

### 5.1 Communication / identity

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 25000 | Reserved | RW | STR | N/A | 1 | 8 | |
| 25008 | Reserved | RW | STR | N/A | 1 | 8 | |
| 25016 | Reserved | RW | STR | N/A | 1 | 8 | |
| 25024 | Router SSID | RW | STR | N/A | 1 | 20 | |
| 25044 | Router password | RW | STR | N/A | 1 | 20 | |
| 25064 | Router encryption method | RW | STR | N/A | 1 | 1 | |
| 25065 | Reserved | RW | STR | N/A | 1 | 10 | |
| 25075 | Domain1 | RW | STR | N/A | 1 | 25 | |
| 25100 | Port number1 | RW | U16 | N/A | 1 | 1 | |
| 25101 | Domain2 | RW | STR | N/A | 1 | 25 | |
| 25126 | Port number2 | RW | U16 | N/A | 1 | 1 | |
| 25127 | Modbus address | RW | U16 | N/A | 1 | 1 | [0–247] |
| 25128 | Manufacturer | RW | STR | N/A | 1 | 4 | |
| 25132 | 485 Modbus baud rate | RW | U32 | N/A | 1 | 2 | [9600, 115200] |

### 5.2 RTC, identity, commands, counters

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 25200 | RTC | RW | U16 | N/A | 1 | 1 | Hbyte = year, Lbyte = month (13–99 / 1–12) |
| 25201 | RTC | RW | U16 | N/A | 1 | 1 | Hbyte = day, Lbyte = hour (1–31 / 0–23) |
| 25202 | RTC | RW | U16 | N/A | 1 | 1 | Hbyte = minute, Lbyte = second (0–59 / 0–59) |
| 25203 | Serial number | RW | STR | N/A | 1 | 8 | ASCII, 16 bytes |
| 25211 | Device type | RW | STR | N/A | 1 | 5 | ASCII, 10 bytes |
| 25216 | Resume factory setting | RW | U16 | N/A | 1 | 1 | [0] |
| 25217 | Clear data | RW | U16 | N/A | 1 | 1 | [0] |
| 25218 | Start (allow connect to grid) | WO | U16 | N/A | 1 | 1 | [0] |
| 25219 | Stop (forbid connect to grid) | WO | U16 | N/A | 1 | 1 | [0] |
| 25220 | Reset | WO | U16 | N/A | 1 | 1 | [0] |
| 25221 | Reset SPS | WO | U16 | N/A | 1 | 1 | |
| 25222 | PV E-Total | RW | U32 | kWh | 10 | 2 | |
| 25224 | PV E-Day | RW | U16 | kWh | 10 | 1 | (U16 since V1.06) |
| 25225 | reserved | RW | U16 | N/A | 1 | 1 | |
| 25226 | E-Total-Sell | RW | U32 | kWh | 10 | 2 | |
| 25228 | h-Total | RW | U32 | h | 1 | 2 | |
| 25230 | E-Day-Sell | RW | U16 | kWh | 10 | 1 | |
| 25231 | E-Total-Buy | RW | U32 | kWh | 10 | 2 | |
| 25233 | E-Day-Buy | RW | U16 | kWh | 10 | 1 | |
| 25234 | E-Total-Load | RW | U32 | kWh | 10 | 2 | |
| 25236 | E-Load-Day | RW | U16 | kWh | 10 | 1 | |
| 25237 | E-BatteryCharge | RW | U32 | kWh | 10 | 2 | |
| 25239 | E-Charge-Day | RW | U16 | kWh | 10 | 1 | |
| 25240 | E-BatteryDischarge | RW | U32 | kWh | 10 | 2 | |
| 25242 | E-discharge-Day | RW | U16 | kWh | 10 | 1 | |

### 5.3 Operation mode and system settings

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 25243 | OperationModeSet | RW | U16 | N/A | 1 | 1 | 0 = self-use; 1 = off-grid; 2 = backup; 3 = ToU; 6 = battery priority; 7 = dynamic trade |
| 25244 | Safety country code | RW | U16 | N/A | 1 | 1 | [0–65535], see Table 8-21 |
| 25245 | ISO | RW | U16 | kΩ | 1 | 1 | ISO limit [0–1000] |
| 25246 | LVRT | RW | U16 | N/A | 1 | 1 | [0,1] |
| 25247 | Islanding | RW | U16 | N/A | 1 | 1 | [0,1] |
| 25248 | ManageModeSet | RW | U16 | N/A | 1 | 1 | 4 = cold start |
| 25249 | burn in reset time | RW | U16 | MIN | 1 | 1 | [0–2880] |
| 25250 | PV start voltage | RW | U16 | V | 10 | 1 | [1800–8500] (i.e. 180.0–850.0 V) |
| 25251 | EnableMPPT4Shadow | RW | U16 | N/A | 1 | 1 | MPPT shadow scan enable (1 on, 0 off) |
| 25252 | BackUpEnable | RW | U16 | N/A | 1 | 1 | Backup output (1 on, 0 off) |
| 25253 | AutoStartBackup | RW | U16 | N/A | 1 | 1 | Off-grid auto startup (1 on, 0 off) |
| 25254 | GridWaveCheckLevel | RW | U16 | N/A | 1 | 1 | 0 = high, 1 = low, 2 = close |
| 25255 | RapaidCutOff | RW | U16 | N/A | 1 | 1 | 0 = off, 1 = on |
| 25256 | BackupStartDly | RW | U16 | N/A | 1 | 1 | Backup start delay |
| 25257 | UpsStdVoltType | RW | U16 | N/A | 1 | 1 | |
| 25258 | Reserved | RW | U16 | N/A | 1 | 1 | |
| 25259 | Burn in mode | RW | U16 | N/A | 1 | 1 | |
| 25260 | Backup overload delay | RW | U16 | s | 1 | 1 | |
| 25261 | UpsPhaseType | RW | U16 | N/A | 1 | 1 | |
| 25262 | OnlyNightDisCharge | RW | U16 | N/A | 1 | 1 | |
| 25263 | DerateRate(VDE) | RW | U16 | N/A | 1 | 1 | e.g. 70 = derate to 70% |
| 25264 | Three Phase unbalanced output | RW | U16 | N/A | 1 | 1 | [0,1]; all power must be turned off and restarted |
| 25265 | Pe Relay CheckEnable | RW | U16 | N/A | 1 | 1 | [0,1] |
| 25266 | HighImpMode | RW | U16 | N/A | 1 | 1 | [0,1] |
| 25267 | BatSpFunc | RW | U16 | N/A | 1 | 1 | |
| 25268 | phase fault clear | RW | U16 | N/A | 1 | 1 | [0,1] |
| 25269 | DCI check coff | RW | U16 | N/A | 1 | 1 | [1–20] |
| 25270 | AFCI Enable | RW | U16 | N/A | 1 | 1 | [0,1] |
| 25271 | ARC self check | WO | U16 | N/A | 1 | 1 | [0x05AA] |
| 25272 | ARC fault remove | WO | U16 | N/A | 1 | 1 | [0x050A] |
| 25273 | Backup Function Lock | WO | U16 | N/A | 1 | 1 | [0–65535] |
| 25274 | OnlineToOfflineSoftStartEn | RW | U16 | N/A | 1 | 1 | [0,1] |
| 25275 | ISOCheckMode | RW | U16 | N/A | 1 | 1 | [0,1] |
| 25276 | OffGridToOnGridDelay | RW | U16 | N/A | 1 | 1 | [10–7200] |
| 25277 | OffGrid Under Voltage Protect Coff | RW | U16 | N/A | 1 | 1 | [50–90] |
| 25278 | BatteryModePvChargeEn | RW | U16 | N/A | 1 | 1 | [0,1] |
| 25279 | DCV check Coef | RW | U16 | N/A | 1 | 1 | [1–20] |
| 25280–25283 | Reserved | RW | U16 | N/A | 1 | 1 each | |
| 25284 | ExtMeterEnable | RW | U16 | N/A | 1 | 1 | |
| 25300 | PowerRatingSet | RW | U16 | N/A | 1 | 1 | [800–10000] |
| 25301–25305 | Reserved | RW | U16 | N/A | 1 | 1 each | |
| 25306 | AcCoupleFuncSet | RW | U16 | N/A | 1 | 1 | [0,1] |
| 25307 | MicroGridFuncSet | RW | U16 | N/A | 1 | 1 | [0,1] |

### 5.4 Battery parameters

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 25350 | LeadBatCapacity | RW | U16 | N/A | 1 | 1 | [25–2000] |
| 25351 | BattStrings | RW | U16 | N/A | 1 | 1 | [4–12] = N |
| 25352 | BattChargeVoltMax | RW | U16 | V | 10 | 1 | [500*N, 600*N] |
| 25353 | BattChargeCurrMax | RW | U16 | A | 10 | 1 | [0–1000] |
| 25354 | BattVoltUnderMin | RW | U16 | V | 10 | 1 | [400*N, 480*N] |
| 25355 | BattDisChgCurrMax | RW | U16 | A | 10 | 1 | [0–1000] |
| 25356 | BattSOCUnderMin | RW | U16 | % | 1 | 1 | [0–100] |
| 25357 | BattOfflineVoltUnderMin | RW | U16 | V | 10 | 1 | [400*N, 480*N] |
| 25358 | BattOfflineSOCUnderMin | RW | U16 | % | – | 1 | [0–100] |
| 25359 | Battery FuncEn Bit | RW | U16 | N/A | – | 1 | BIT0 = StopSocProtect |
| 25360 | Clear battery setting | WO | U16 | – | – | 1 | |
| 25361 | BattStringVoltRated | RW | U16 | V | 10 | 1 | |
| 25362 | BattSOCMaxCharge | RW | U16 | % | 1 | 1 | [0–100] |
| 25363 | BattOfflineSOCMaxCharge | RW | U16 | % | 1 | 1 | [0–100] |

### 5.5 Safety / grid protection

All "decided by specific safety regulations". "periods" = time unit used for protection times.

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 25400 | GRID frequency | R | U16 | – | – | 1 | 0 = 50 Hz, 1 = 60 Hz |
| 25401 | GridVoltHighS1 | RW | U16 | V | 10 | 1 | |
| 25402 | GridVoltHighS1Time | RW | U16 | periods | 1 | 1 | |
| 25403 | GridVoltLowS1 | RW | U16 | V | 10 | 1 | |
| 25404 | GridVoltLowS1Time | RW | U16 | periods | 1 | 1 | |
| 25405 | GridVoltHighS2 | RW | U16 | V | 10 | 1 | |
| 25406 | GridVoltHighS2Time | RW | U16 | periods | 1 | 1 | |
| 25407 | GridVoltLowS2 | RW | U16 | V | 10 | 1 | |
| 25408 | GridVoltLowS2Time | RW | U16 | periods | 1 | 1 | |
| 25409 | GridVoltHighS3 | RW | U16 | V | 10 | 1 | |
| 25410 | GridVoltHighS3Time | RW | U16 | periods | 1 | 1 | |
| 25411 | GridVoltLowS3 | RW | U16 | V | 10 | 1 | |
| 25412 | GridVoltLowS3Time | RW | U16 | periods | 1 | 1 | |
| 25413 | GridVoltQualit | RW | U16 | V | 10 | 1 | |
| 25414 | GridFreqHighS1 | RW | U16 | Hz | 100 | 1 | |
| 25415 | GridFreqHighS1Time | RW | U16 | periods | 1 | 1 | |
| 25416 | GridFreqLowS1 | RW | U16 | Hz | 100 | 1 | |
| 25417 | GridFreqLowS1Time | RW | U16 | periods | 1 | 1 | |
| 25418 | GridFreqHighS2 | RW | U16 | Hz | 100 | 1 | |
| 25419 | GridFreqHighS2Time | RW | U16 | periods | 1 | 1 | |
| 25420 | GridFreqLowS2 | RW | U16 | Hz | 100 | 1 | |
| 25421 | GridFreqLowS2Time | RW | U16 | periods | 1 | 1 | |
| 25422 | GridVoltHigh | RW | U16 | V | 10 | 1 | |
| 25423 | GridVoltLow | RW | U16 | V | 10 | 1 | |
| 25424 | GridFreqHigh | RW | U16 | Hz | 100 | 1 | |
| 25425 | GridFreqLow | RW | U16 | Hz | 100 | 1 | |
| 25426 | GridStartTime | RW | U16 | s | 1 | 1 | |
| 25427 | GridVoltRecoverHigh | RW | U16 | V | 10 | 1 | |
| 25428 | GridVoltRecoverLow | RW | U16 | V | 10 | 1 | |
| 25429 | GridFreqRecoverHigh | RW | U16 | Hz | 100 | 1 | |
| 25430 | GridFreqRecoverLow | RW | U16 | Hz | 100 | 1 | |
| 25431 | GridOverVoltRecoverTime | RW | U16 | s | 1 | 1 | |
| 25432 | GridUnderVoltRecoverTime | RW | U16 | s | 1 | 1 | |
| 25433 | GridOverFreqRecoverTime | RW | U16 | s | 1 | 1 | |
| 25434 | GridUnderFreqRecoverTime | RW | U16 | s | 1 | 1 | |
| 25435 | Power Slope (generate) | RW | U16 | s | 1 | 1 | Power slope |
| 25436 | Power Slope (OverVolt reconnect) | RW | U16 | s | 1 | 1 | |
| 25437 | Power Slope (UnderVolt reconnect) | RW | U16 | s | 1 | 1 | |
| 25438 | Power Slope (OverFreq reconnect) | RW | U16 | s | 1 | 1 | |
| 25439 | Power Slope (UnderFreq reconnect) | RW | U16 | s | 1 | 1 | |
| 25440 | Power rate limit (reduction) | RW | U16 | s | 1 | 1 | |
| 25441 | Power charge limit (generate) | RW | U16 | s | 1 | 1 | |
| 25442 | Power charge limit (reconnect) | RW | U16 | s | 1 | 1 | |
| 25443 | GridFuncEnBitEE | RW | U16 | NA | 1 | 1 | bit1 = power slope enable |

### 5.6 cos φ(P) curve

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 25444 | EnableCurve | RW | U16 | – | 1 | 1 | 1 = enable, 0 = disable |
| 25445 | PointAValue | RW | U16 | W | 1 | 1 | |
| 25446 | PointA_PF | RW | U16 | % | 100 | 1 | |
| 25447 | PointBValue | RW | U16 | W | 1 | 1 | |
| 25448 | PointB_PF | RW | U16 | % | 100 | 1 | |
| 25449 | PointCValue | RW | U16 | W | 1 | 1 | |
| 25450 | PointC_PF | RW | U16 | % | 100 | 1 | |
| 25451 | PointDValue | RW | U16 | W | 1 | 1 | |
| 25452 | PointD_PF | RW | U16 | % | 100 | 1 | |
| 25453 | lock in voltage | RW | U16 | V | 10 | 1 | [2300–2530] |
| 25454 | lock out voltage | RW | U16 | V | 10 | 1 | [2070–2300] |
| 25455 | lock out power | RW | S16 | W | 1 | 1 | [-11000, 11000] |

### 5.7 Power–frequency curve

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 25456 | EnableCurve | RW | U16 | – | 1 | 1 | bit0: 0 = off, 1 = on; bit1 (response mode): 1 = fstop, 0 = slope |
| 25457 | Ffrozen-DCH (frequency of Pm) | RW | U16 | Hz | 100 | 1 | fstop |
| 25458 | Ffrozen-CH (frequency of Pm) | RW | U16 | Hz | 100 | 1 | |
| 25459 | fstop-DCH | RW | U16 | Hz | 100 | 1 | |
| 25460 | fstop-CH | RW | U16 | Hz | 100 | 1 | |
| 25461 | Recovery waiting time | RW | U16 | s | 1 | 1 | |
| 25462 | Recovery frequency1 | RW | U16 | Hz | 100 | 1 | |
| 25463 | Recovery frequency2 | RW | U16 | Hz | 100 | 1 | |
| 25464 | Recovery slope | RW | U16 | – | 1 | 1 | |
| 25465 | Ffrozen-DCH (frequency of Pm) | RW | U16 | Hz | 100 | 1 | slope |
| 25466 | Ffrozen-CH (frequency of Pm) | RW | U16 | Hz | 100 | 1 | |
| 25467 | down slope power reference | RW | U16 | – | 1 | 1 | |
| 25468 | down slope | RW | U16 | – | 1 | 1 | |

### 5.8 QU curve

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 25469 | EnableCurve | – | U16 | – | – | 1 | |
| 25470 | lock in power | RW | U16 | W | 1 | 1 | |
| 25471 | lock out power | RW | U16 | W | 1 | 1 | |
| 25472 | V1 voltage | RW | U16 | V | 10 | 1 | |
| 25473 | V1 value (var % rated VA) | RW | U16 | W | 1 | 1 | |
| 25474 | V2 voltage | RW | U16 | V | 10 | 1 | |
| 25475 | V2 value (var % rated VA) | RW | U16 | W | 1 | 1 | Select one set: K value, or V2 & V3 values |
| 25476 | V3 voltage | RW | U16 | V | 10 | 1 | |
| 25477 | V3 value (var % rated VA) | RW | U16 | W | 1 | 1 | Select one set: K value, or V2 & V3 values |
| 25478 | V4 voltage | RW | U16 | V | 10 | 1 | |
| 25479 | V4 value (var % rated VA) | RW | U16 | W | 1 | 1 | |
| 25480 | K value | RW | U16 | – | 1 | 1 | Select one set: K value, or V2 & V3 values |
| 25481 | time constant | RW | U16 | – | 1 | 1 | |
| 25482 | Miscellanea | RW | U16 | – | – | 1 | |
| 25483 | Rated Voltage (Korea) | RW | U16 | – | – | 1 | |
| 25484 | response time (Korea) | RW | U16 | – | – | 1 | |

### 5.9 PU curve, fixed power, grid limit (Japan), tests

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 25485 | PU curve | RW | U16 | – | 1 | 1 | |
| 25486 | Power change rate | RW | U16 | – | – | 1 | |
| 25487 | V1 voltage | RW | U16 | V | 10 | 1 | |
| 25488 | V1 value ((P/Pn)%) | RW | S16 | – | 10 | 1 | |
| 25489 | V2 voltage | RW | U16 | V | 10 | 1 | |
| 25490 | V2 value ((P/Pn)%) | RW | S16 | – | 10 | 1 | |
| 25491 | V3 voltage | RW | U16 | V | 10 | 1 | |
| 25492 | V3 value ((P/Pn)%) | RW | S16 | – | 10 | 1 | |
| 25493 | V4 voltage | RW | U16 | V | 10 | 1 | |
| 25494 | V4 value ((P/Pn)%) | RW | S16 | – | 10 | 1 | |
| 25495 | Fixed Power Factor | RW | U16 | – | 100 | 1 | Refers to Table 8-18 (not included in the PDF) |
| 25496 | Fixed reactive power | RW | U16 | – | 10 | 1 | |
| 25497 | Fixed active power | RW | U16 | – | 10 | 1 | 0.1% |
| 25498 | GridLimitByVolStartVol | RW | U16 | V | 10 | 1 | Grid limit start voltage (Japan) |
| 25499 | GridLimitByVolStartPer | RW | U16 | % | 1 | 1 | Grid limit start percent (Japan) |
| 25500 | GridLimitByVolSlope | WO | U16 | %/V | 1 | 1 | Grid limit slope (Japan) |
| 25501 | Auto Test Enable | WO | U16 | – | – | 1 | 0 = stop, 1 = start |
| 25502 | Auto Test step | WO | U16 | – | – | 1 | 0–8 |
| 25503 | uwItalyFreqMode | RW | U16 | – | – | 1 | |
| 25504 | All Power Curve Disable | RW | U16 | – | – | 1 | [0,1] |
| 25505 | R phase fixed active power | RW | U16 | ‰ | 1 | 1 | [0–1000] |
| 25506 | S phase fixed active power | RW | U16 | ‰ | 1 | 1 | [0–1000] |
| 25507 | T phase fixed active power | RW | U16 | ‰ | 1 | 1 | [0–1000] |

### 5.10 ZVRT (zero/low/high voltage ride-through)

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 25508 | ZvrtConfig | RW | U16 | – | – | 1 | 0 = disable; 1 = only LVRT; 2 = only HVRT; 3 = both |
| 25509 | LvrtStartVolt | RW | U16 | V | 10 | 1 | [0–2300] |
| 25510 | LvrtEndVolt | RW | U16 | V | 10 | 1 | [0–2300] |
| 25511 | LvrtStartTripTime | RW | U16 | periods | 1 | 1 | [1–65535] |
| 25512 | LvrtEndTripTime | RW | U16 | periods | 1 | 1 | [1–65535] |
| 25513 | LvrtTripLimitVolt | RW | U16 | V | 10 | 1 | [0–2300] |
| 25514 | HvrtStartVolt | RW | U16 | V | 10 | 1 | [2300–3000] |
| 25515 | HvrtEndVolt | RW | U16 | V | 10 | 1 | [2300–3000] |
| 25516 | HvrtStartTripTime | RW | U16 | periods | 1 | 1 | [1–65535] |
| 25517 | HvrtEndTripTime | RW | U16 | periods | 1 | 1 | [1–65535] |
| 25518 | HvrtTripLimitVolt | RW | U16 | V | 10 | 1 | [2300–3000] |
| 25519 | PF time constant | RW | U16 | NA | 1 | 1 | [0–4096] |
| 25520 | Power Freq time constant | RW | U16 | NA | 1 | 1 | [0–4096] |
| 25521 | PU time constant | RW | U16 | NA | 1 | 1 | [0–4096] |
| 25522 | GridFuncEnBit | RW | U16 | NA | 1 | 1 | Bit0 = grid protect |

### 5.11 EMS manage data (external EMS control, work schedules)

| Addr | Name | R/W | Type | Unit | Mult | Regs | Remark |
|---|---|---|---|---|---|---|---|
| 27500 | StopSocProtect | RW | U16 | – | – | 1 | [0,1] |
| 27501 | BattFloatVolt | RW | U16 | V | 10 | 1 | [500*N, 600*N], N = battery strings |
| 27502 | BattFloatCurr | RW | U16 | A | 10 | 1 | [0–100] |
| 27503 | BattToFloatTime | RW | U16 | MIN | 1 | 1 | [10–30] |
| 27504 | BattTypeIndex | RW | U16 | – | – | 1 | [0–511], see Table 8-23 |
| 27505 | ManufacturerCode | RW | U16 | – | – | 1 | |
| 27506 | DCVoltOutput / KeepBattVoltOn | RW | U16 | – | – | 1 | |
| 27507 | BattAvgChgVolt | RW | U16 | V | 10 | 1 | |
| 27508 | BatAvgChgHours | RW | U16 | H | 1 | 1 | |
| 27509 | FeedPowerEnable | RW | U16 | – | – | 1 | [0,1] |
| 27510 | FeedPowerPara | RW | U16 | W | 1 | 1 | [0–10000] |
| 27511 | EMSPowerMode | RW | U16 | – | – | 1 | See Table 8-16. V1.15 added mode **16** (= 0x0010, battery charge-only self-use) |
| 27512 | EMSPowerSet | RW | U16 | W | 1 | 1 | [0–60000] |
| 27513 | Reserved | RW | U16 | NA | 1 | 1 | |
| 27514 | Battery protocol | RW | U16 | – | – | 1 | [0–511], see Table 8-23 |
| 27515 | StartTime_1 | RW | U16 | HH:MM | – | 1 | HH = value/100, MM = value%100; [0–23],[0–59] |
| 27516 | EndTime_1 | RW | U16 | HH:MM | – | 1 | same encoding |
| 27517 | BatPowerPercent_1 | RW | U16 | % | – | 1 | [-100, 100] (negative/positive = charge/discharge direction, not specified in source) |
| 27518 | WorkWeek_1 | RW | U16 | – | – | 1 | Table 8-20 |
| 27519 | StartTime_2 | RW | U16 | HH:MM | – | 1 | |
| 27520 | EndTime_2 | RW | U16 | HH:MM | – | 1 | |
| 27521 | BatPowerPercent_2 | RW | U16 | % | – | 1 | [-100, 100] |
| 27522 | WorkWeek_2 | RW | U16 | – | – | 1 | Table 8-20 |
| 27523 | StartTime_3 | RW | U16 | HH:MM | – | 1 | |
| 27524 | EndTime_3 | RW | U16 | HH:MM | – | 1 | |
| 27525 | BatPowerPercent_3 | RW | U16 | % | – | 1 | [-100, 100] |
| 27526 | WorkWeek_3 | RW | U16 | – | – | 1 | Table 8-20 |
| 27527 | StartTime_4 | RW | U16 | HH:MM | – | 1 | |
| 27528 | EndTime_4 | RW | U16 | HH:MM | – | 1 | |
| 27529 | BatPowerPercent_4 | RW | U16 | % | – | 1 | [-100, 100] |
| 27530 | WorkWeek_4 | RW | U16 | – | – | 1 | Table 8-20 |
| 27531 | SOC start to force charge | RW | U16 | – | – | 1 | |
| 27532 | SOC stop force charge | RW | U16 | – | – | 1 | |
| 27533 | Clear all economic mode | WO | U16 | – | – | 1 | 1 = CLEAR |
| 27534 | 3 Phase FeedPowerEnable | RW | U16 | – | – | 1 | [0,1] |
| 27535 | R phase FeedPowerPara | RW | U16 | W | 1 | 1 | [0–5000] |
| 27536 | S phase FeedPowerPara | RW | U16 | W | 1 | 1 | [0–5000] |
| 27537 | T phase FeedPowerPara | RW | U16 | W | 1 | 1 | [0–5000] |
| 27547 | effective Time of EMSPowerMode | RW | U16 | s | 1 | 1 | [1–65535] = effective for that many seconds, then expires; [0] = permanent (until power loss/reboot). Added V1.15 for third-party EMS |
| 27548 | ExitModeSet | RW | U16 | – | – | 1 | Mode to return to when EMSPowerMode expires: 0 = self-use; 1 = off-grid; 2 = backup; 3 = ToU; 6 = battery priority; 7 = AI optimization mode; 255 = restore the previous operating mode. Added V1.15 (the change log misprints the address as "275448") |

---

## 6. Attached tables

(Table numbers follow the source. Tables 8-5, 8-6, 8-18 and 8-19 are referenced or implied but not present in the PDF; Table 8-12 is present but empty.)

### Table 8-1 Work State (register 176)

| Code | Mode | Description |
|---|---|---|
| 0x00 | Wait | Cut off all connections to the inverter |
| 0x01 | On-Grid | PV inputs to inverter, inverter outputs to grid |
| 0x02 | Off-Grid | PV inputs to inverter (1st), battery inputs to inverter (2nd), inverter works as AC source |
| 0x03 | Fault | Fault mode |
| 0x04 | Flash | Inverter upgrade |
| 0x05 | Check | Power-on self-check of inverter |

### Table 8-2 Error Message (registers 177/178, 32-bit bitfield; 177 = low word, 178 = high word)

| Bit | Error message | Description |
|---|---|---|
| 31 | Internal Communication Failure | Communication between microcontrollers failed |
| 30 | EEPROM R/W Failure | EEPROM cannot be read or written |
| 29 | Relay Check Failure | Relay check failed |
| 28 | DSP communication failure | Communication between ARM and DSP failed |
| 27 | Fac High Failure | Grid frequency too high |
| 26 | Fac Low Failure | Grid frequency too low |
| 25 | Vac High Failure | Grid voltage too high |
| 24 | Vac Low Failure | Grid voltage too low |
| 23 | Vac Consistency Failure | Master/slave grid voltage differ |
| 22 | Fac Consistency Failure | Master/slave grid frequency differ |
| 21 | (unnamed in source) | |
| 20 | Back-Up Over Load | Back-Up output overloaded |
| 19 | DC Injection High | DC injection to grid too high |
| 18 | Isolation Failure | Isolation resistance of PV plant out of tolerable range |
| 17 | Micro Electronic Failure | |
| 16 | (unnamed in source) | |
| 15 | PV Over Voltage | PV input voltage above tolerable maximum |
| 14 | Utility Phase Failure | |
| 13 | Over Temperature | Temperature too high |
| 12 | Fan Failure | |
| 11 | DC Bus High | DC bus too high |
| 10 | Ground I Failure | Ground current too high |
| 9 | Utility Loss | Utility unavailable |
| 8 | HCT Failure | HCT abnormal by multi-self-test |
| 7 | Relay Failure | Relay abnormal by multi-self-test |
| 6 | GFCI Failure | GFCI device abnormal by multi-self-test |
| 5 | AFCI Device Check Failure | AFCI detecting circuit abnormal |
| 4 | GFCI Consistency Failure | Master/slave GFCI values differ |
| 3 | DCI Consistency Failure | Master/slave output DC current values differ |
| 2 | AFCI Failure | AFCI check failure |
| 1 | AC HCT Check Failure | Output current sensor abnormal |
| 0 | GFCI Device Check Failure | GFCI detecting circuit abnormal |

**Error Message EX** (registers 179/180). Only these bits are named; all others are blank/reserved in the source:

| Bit | Name |
|---|---|
| 12 | FactoryConfigFault |
| 9 | EMS Comm Loss |
| 7 | PV Connect Fault |
| 4 | Temp check Fault |
| 3 | MeterCTFault_Ext |
| 1 | Box Fault |
| 0 | Ref Voltage Fault |

### Table 8-3 PV Mode (register 115)

| Bits | Description |
|---|---|
| 0–1 | PV1 mode (code per Table 8-4) |
| 2–3 | PV2 mode |
| 4–5 | PV3 mode |
| 6–7 | PV4 mode |

### Table 8-4 PV Mode Code

| Code | Description |
|---|---|
| 0x00 | No PV, inverter disconnected from PV |
| 0x01 | Standby, PV does not output power |
| 0x02 | Work, PV outputs power |

### Table 8-7 BMS Alarm Code (registers 2006 = bits 0–15, 2007 = bits 16–31)

| Bit | Alarm |
|---|---|
| 31–21 | Reserved |
| 20 | AFE comm Fail |
| 19 | TempSampleFail |
| 18 | CurrentSampleFail |
| 17 | Volt sample Fail |
| 16 | Parallel Fail |
| 15 | Charging over-voltage 3 |
| 14 | Discharge under-voltage 3 |
| 13 | Cell High temperature 3 |
| 12 | Communication failure 2 |
| 11 | Charging circuit Failure |
| 10 | Discharge circuit Fault |
| 9 | Battery Lock |
| 8 | Battery break |
| 7 | DC bus fault |
| 6 | Precharge fault |
| 5 | Discharging overcurrent 2 |
| 4 | Charging overcurrent 2 |
| 3 | Cell Low temperature 2 |
| 2 | Cell High temperature 2 |
| 1 | Discharging under-voltage 2 |
| 0 | Charging over-voltage 2 |

(The source's header row says "Bit31~23 … Bit22 Bit21 Bit20 …": bits 31–21 are reserved, 20–16 are named above.)

### Table 8-8 BMS Warning Code (registers 2008 = bits 0–15, 2009 = bits 16–31)

Low byte (clear in source):

| Bit | Warning |
|---|---|
| 7 | System Reboot |
| 6 | communication failure 1 |
| 5 | Discharging over-current 1 |
| 4 | Charging over-current 1 |
| 3 | Cell Low temperature 1 |
| 2 | Cell High temperature 1 |
| 1 | Discharge under-voltage 1 |
| 0 | Charging over-voltage 1 |

High byte **[AMBIGUOUS]**: the source header lists Bit31~15, Bit14, Bit13, Bit12, Bit11, Bit10, Bit9, Bit8 but only five values: `Reserved`, `System High temperature`, `System Low temperature2`, `System Low temperature1`, `Cellimbalance`. The exact bit-to-name mapping could not be recovered from the text; check PDF page 26.

### Table 8-9 Battery Status (registers 173, 265)

| Code | Description |
|---|---|
| 0x00 | No battery, inverter disconnected from battery |
| 0x01 | Standby, no discharging and no charging |
| 0x02 | Discharging |
| 0x03 | Charging |
| 0x04 | Waiting for charge |
| 0x05 | Waiting for discharge |

### Table 8-10 Grid Status (register 132)

| Code | Description |
|---|---|
| 0x01 | OK, inverter connected to grid |
| 0x02 | Fault, something is wrong |

### Table 8-11 Backup Status (registers 142, 148, 154)

| Code | Description |
|---|---|
| 0x00 | ON, inverter connected to load |
| 0x01 | OFF, inverter disconnected from load |

### Table 8-12 Operation Mode

Empty in the source (see register 214 / 25243 for the mode codes).

### Table 8-13 Energy Status

| Code | Description |
|---|---|
| 0x00 | Inverter neither sends power to grid nor gets power from grid |
| 0x01 | Inverter sends power to grid |
| 0x02 | Inverter gets power from grid |

### Table 8-14-1 Diagnose Info (registers 202 = low word, 203 = high word; 32-bit bitfield)

The source has a "Type" column with merged cells (Affect discharge / Affect charging / Other) whose boundaries are **[AMBIGUOUS]**; best reading: bits 0–14 affect discharge, bits 15–18 affect charging, bit 19 affects discharge, bits 20 onward "other".

| Bit | Name | Explanation |
|---|---|---|
| 0 | BatteryVoltLow | Battery not discharging because of low battery voltage |
| 1 | BatterySOCLow | Battery not discharging because of low SOC |
| 2 | BatterySOCInBack | Battery SOC has not recovered to the allow-discharge level |
| 3 | BMSDischargeDisable | BMS does not allow discharge |
| 4 | DischargeTimeOn | Discharge time is set (1 on, 0 off) |
| 5 | ChargeTimeOn | Charge time is set (1 on, 0 off) |
| 6 | DischargeDriveOn | Discharge driver is turned on |
| 7 | BMSDischgCurrentLow | BMS discharge current limit too low |
| 8 | DischargeCurrentLow | Discharge current limit too low (from app) |
| 9 | MeterCommLoss | Smart meter communication failure |
| 10 | MeterConnectReverse | Smart meter connection reversed |
| 11 | SelfUseLoadLight | Load power too low to activate battery discharge |
| 12 | EMSDischargeIZero | Discharge current limit is 0 A from EMS |
| 13 | DischargeBUSHigh | Battery not discharging because PV voltage is too high |
| 14 | BatteryDisconnect | Battery disconnected |
| 15 | BatteryOvercharge | Battery overcharged |
| 16 | BMSOverTemperature | Lithium battery over temperature |
| 17 | BMSOvercharge | Lithium battery overcharged, or an individual cell voltage is higher |
| 18 | BMSChargeDisable | BMS does not allow charge |
| 19 | SelfUseOff | Self-use mode turned off |
| 20 | SOCDeltaOverRange | SOC jumps abnormally |
| 21 | BatterySelfDischarge | Battery discharges at low current for a long time, continuously over 30% of battery SOC |
| 22 | OffgridSOCLow | SOC is low in off-grid state |
| 23 | GridWaveUnstable | Grid wave is bad, switching to back-up mode frequently |
| 24 | FeedPowerLimit | Export power limit is set |
| 25 | PFValueSet | PF value is set |
| 26 | RealPowerLimit | Active power value is set |
| 27 | DCOutputOn | |
| 28 | SOCProtectOff | |
| 29 | Discharge mode for BP | |
| 30 | BmsMustCharge | |
| 31 | FanSpeedLow | |

### Table 8-14-2 DiagnoseEx Info (registers 204 = low word, 205 = high word)

| Bit | Name | Explanation |
|---|---|---|
| 0 | BattSpsRelayOff | Battery SPS relay is off |
| 1 | BypassRelayDeadClose | Bypass relay is dead-closed |
| 2 | BattBmsCommLoss | Battery BMS communication lost |
| 3 | BackupFuncOn | Backup function is ON |
| 4 | BoxCommLoss | Box communication lost |
| 5 | DRED0ForceOff | 0 = normal, 1 = force off |
| 6 | ExtCTUninstalled | 0 = installed, 1 = uninstalled |
| 7 | BatInternalCommLoss | 0 = normal, 1 = loss |
| 8 | BatteryReady | 0 = not ready, 1 = ready |
| 9 | Parallel | 0 = standalone, 1 = parallel |
| 10 | ParLeader | 0 = slave, 1 = leader |
| 11 | ParallelPhase | 0 = 1 phase; 1 = R of 3 phase; 2 = S of 3 phase; 3 = T of 3 phase (spans bits 11–12) |
| 12 | (part of ParallelPhase / unnamed) | |
| 13 | BoxUninstalled | 0 = installed, 1 = uninstalled |

### Table 8-15 DRM Status (register 2000)

| Bit | Name | Description |
|---|---|---|
| 0–8 | DRM0 … DRM8 | Switch: 1 = ON, 0 = OFF (bit n = DRMn) |
| 9–14 | (unnamed) | |
| 15 | DRED Connect Status | 1 = connected, 0 = disconnected |

### Table 8-16 EMS Power Mode (registers 27511 `EMSPowerMode`, 27512 `EMSPowerSet`)

Write the **Command** code to 27511 and the power value (W) to 27512. Related: 27547 sets how long the mode stays active, 27548 selects the mode to fall back to.

> `Xmax` = upper limit of the power control value (actual power is adjusted to working conditions). `Xset` = target value of power control (actual power must reach the set value). For low-priority energy sources, load is reduced first when battery charge power or inverter rated output is limited.
>
> The PDF's "PV / Grid / Bat" priority columns (colour-coded green in the original) were garbled by text extraction **[AMBIGUOUS]**, so the priority text below is listed as extracted. Authoritative information is the `PBattery` formula and note.

| Scenario | Mode | Command (hex / dec) | EMSPowerSet meaning | Priority text as extracted | Behaviour / formula |
|---|---|---|---|---|---|
| System shutdown | Stopped | 0x00FF / 255 | NA | | Stop working and switch to wait mode |
| Self-use | Auto | 0x0001 / 1 | NA | | `PBattery = PInv − Pmeter − Ppv` (discharge/charge). Battery power is controlled by the meter power when meter communication is normal |
| Charge-only self-use | Charge Only Self-use | 0x0010 / 16 | NA | | `PBattery = PInv − Pmeter − Ppv` (charge only). Battery is not allowed to discharge; it can only charge from excess PV. Added in V1.15 (27511 mode 16) |
| Self-use | Self-use | 0x0011 / 17 | NA | | `PBattery = PInv − Pmeter − Ppv` (discharge/charge). Meter-controlled when meter comm is normal. Added V1.15 (2026-07-08) |
| Keep battery charging | Charge-PV | 0x0002 / 2 | Xmax | High, Low[1], Energy In | `PBattery = Xmax + PV` (charge). Xmax = power allowed to be taken from grid; PV preferred. When 0, only PV is used. Limited by charging current limit |
| Keep battery discharging | Dischg+PV | 0x0003 / 3 | Xmax | High, Energy Out, Low | `PBattery = Xmax` (discharge). Xmax = allowable battery discharge power. When grid feed-in is limited, PV is used first |
| Grid scheduling (inverter as unit) | Import-AC | 0x0004 / 4 | Xset | Low, High, Energy In | `PBattery = Xset + PV` (charge). Xset = power purchased from grid; grid purchase preferred. If PV is too large, MPPT power is limited (grid-side load not considered) |
| Grid scheduling | Export-AC | 0x0005 / 5 | Xset | High, Energy Out, Low | `PBattery = Xset` (discharge). Xset = power sold to grid; PV preferred, battery discharges when PV is insufficient. PV limited by X (grid-side load not considered) |
| Off-grid reservation | Conserve | 0x0006 / 6 | NA | | `PBattery = PV` (charge). In on-grid mode the battery is continuously charged using only PV (AC-couple model takes 10% of rated grid power). Battery can only discharge in off-grid mode |
| Off-grid mode | Off-Grid | 0x0007 / 7 | NA | | `PBattery = Pbackup − Ppv` (charge/discharge). Forced off-grid operation |
| No-battery mode (hybrid) | Battery standby | 0x0008 / 8 | NA | | `PBattery = 0` (standby). Battery neither charges nor discharges |
| Regional energy management | Buy Power | 0x0009 / 9 | Xset | Low, High, Energy In/Out | `PBattery = PInv − (Pmeter + Xset) − Ppv` (charge/discharge). With normal meter comm, purchased grid power is controlled to Xset. If PV too large, MPPT is limited; if load too large, battery discharges |
| Regional energy management | Sell Power | 0x000A / 10 | Xset | High, Energy Out, Low | `PBattery = PInv − (Pmeter − Xset) − Ppv` (charge/discharge). With normal meter comm, power sold to grid is controlled to Xset; PV preferred, battery discharges when PV is insufficient; PV limited by Xset |
| Force battery to set power | Charge-BAT | 0x000B / 11 | Xset | High, Low, Energy In | `PBattery = Xset` (charge). Xset = battery charge power; PV preferred, buys from grid if PV insufficient. Also limited by charge current limit |
| Force battery to set power | Discharge-BAT | 0x000C / 12 | Xset | Low, Energy In, High | `PBattery = Xset` (discharge). Xset = battery discharge power; battery discharge has priority; if PV too large MPPT is limited. Also limited by discharge current limit |

### Table 8-17 CPLD Warning Code (register 201)

| Value | Message |
|---|---|
| 1 | PV1 Over Current HW |
| 2 | PV2 Over Current HW |
| 3 | Battery Over Current HW |
| 4 | Bus Over Voltage HW |
| 5 | R InvOverCurr HW |
| 6 | S InvOverCurr HW |
| 7 | T InvOverCurr HW |
| 8 | BatRelayFail |

### Table 8-20 Weekly schedule (registers 27518, 27522, 27526, 27530)

| Bits | Definition |
|---|---|
| High byte (bits 15–8) | 0xFF = enable, 0x00 = disable |
| Bit 7 | NA |
| Bit 6 | Saturday |
| Bit 5 | Friday |
| Bit 4 | Thursday |
| Bit 3 | Wednesday |
| Bit 2 | Tuesday |
| Bit 1 | Monday |
| Bit 0 | Sunday |

Example: `0xFF7F` = enabled, all 7 days.

### Table 8-21 Safety Code (registers 175, 25244)

| Code | Description | Grid connection standard |
|---|---|---|
| 0 | 50Hz Grid Default | Default |
| 1 | 50Hz LV Default | 50Hz LV Default |
| 2 | 60Hz Grid Default | CSA |
| 3 | 60Hz LV Default | 60Hz LV Default |
| 4 | Argentina | |
| 5 | AU_Endeavour | |
| 6 | Australia | AS/NZS 4777.2 |
| 7 | Australia Ausgrid | AS/NZS 4777.2 |
| 8 | Australia Energex | AS/NZS 4777.2 |
| 9 | Australia Ergon | AS/NZS 4777.2 |
| 10 | Australia Essential | AS/NZS 4777.2 |
| 11 | Australia GreenGrid | AS/NZS 4777.2 |
| 12 | Australia Horizon | AS/NZS 4777.2 |
| 13 | Australia MicroGrid | AS/NZS 4777.2 |
| 14 | Australia Pwcore_CitiPW | AS/NZS 4777.2 |
| 15 | Australia SAPN | AS/NZS 4777.2 |
| 16 | Australia Western | AS/NZS 4777.2 |
| 17 | AustraliaL | AS/NZS 4777.2 |
| 18 | Austria | Un: 230Vac |
| 19 | Barbados | Un: 230Vac |
| 20 | Belgium C10/C11 | Un: 230Vac |
| 21 | Brazil | Un: 220Vac |
| 22 | Brazil LV | Un: 220Vac |
| 23 | Bulgaria | EN50438 |
| 24 | CEI_016 | CEI-016 (Un: 230Vac) |
| 25 | Chile BISI 4.0 | Un: 220Vac |
| 26 | China NB-T | |
| 27 | China HHV NB-T | |
| 28 | China HV NB-T | |
| 29 | China Station NB-T | |
| 30 | China HongKong | |
| 31 | Cyprus | Un: 230Vac |
| 32 | Czech | EN50438(CZ) (Un: 230Vac) |
| 33 | Danmark | EN50438(DK) |
| 34 | DEWA LV | DEWA (Un: 230Vac) |
| 35 | DEWA MV | DEWA (Un: 230Vac) |
| 36 | Energe30K | Un: 230Vac |
| 37 | Ergon30K | Un: 230Vac |
| 38 | France | VDE0126 |
| 39 | French 50Hz | Un: 230Vac |
| 40 | French 60Hz | Un: 230Vac |
| 41 | G59/3 | G59/3 (Un: 230Vac) |
| 42 | G83/G59 | G83/2 G59/3 (Un: 230Vac) |
| 43 | Germany | VDE-AR-N 4105 (Un: 230Vac) |
| 44 | Germany_B | |
| 45 | GreeceMainland | EN50438(GR) (Un: 230Vac) |
| 46 | Holland | EN50438 |
| 47 | Holland 16/20A | EN50438 |
| 48 | Holland_MV | |
| 49 | Hungary | Un: 230Vac |
| 50 | IEC61727_60Hz | IEC61727 (Un: 230Vac) |
| 51 | IEEE1547 208Vac | IEEE1547 (Un: 120/208Vac) |
| 52 | IEEE1547 220Vac | IEEE1547 (Un: 127/220Vac) |
| 53 | IEEE1547 230Vac | IEEE1547 (Un: 230/400Vac) |
| 54 | IEEE1547 240Vac | IEEE1547 (Un: 138.6/240Vac) |
| 55 | India | IEC61727 |
| 56 | India Higher | IEC61727 (Un: 230Vac) |
| 57 | Ireland | EN50438 Ireland |
| 58 | Italy ENEL | Un: 230Vac |
| 59 | JP_50Hz | JP_50Hz |
| 60 | JP_60Hz | JP_60Hz |
| 61 | Korea | Un: 220Vac |
| 62 | Mauritius | Un: 230Vac |
| 63 | NewZealand | AS/NZS 4777.2 |
| 64 | Northern Ireland | Northern Ireland |
| 65 | Philippines | Philippines |
| 66 | Poland | EN50438 |
| 67 | Poland_MV | |
| 68 | Romania | Un: 230Vac |
| 69 | Slovakia | EN50438(SV) (Un: 230Vac) |
| 70 | South Africa | Un: 230Vac |
| 71 | Spain | RD1699 (Un: 230Vac) |
| 72 | Spain_MV | |
| 73 | SpainIslands | RD1699 (Un: 230Vac) |
| 74 | SriLanka | Un: 230Vac |
| 75 | Sweden | EN50438 (Un: 230Vac) |
| 76 | Sweden_MV | |
| 77 | Switzerland | VDE-AR-N 4105 (Un: 230Vac) |
| 78 | Taiwan | Un: 230Vac |
| 79 | Thailand MEA | MEA |
| 80 | Thailand PEA | PEA |
| 81 | VDE4110 | |
| 82 | Warehouse | Warehouse |
| 83 | USA_208VacDefault | |
| 84 | USA_240VacDefault | |
| 85 | USA_208VacCA_SCE | |
| 86 | USA_240VacCA_SCE | |
| 87 | USA_208VacCA_SDGE | |
| 88 | USA_240VacCA_SDGE | |
| 89 | USA_208VacCA_PGE | |
| 90 | USA_240VacCA_PGE | |
| 91 | USA_208VacHECO_14HO | |
| 92 | USA_240VacHECO_14HO | |
| 93 | USA_208VacHECO_14HM | |
| 94 | USA_240VacHECO_14HM | |
| 95 | USA_480VacDefault | |
| 96 | USA_480VacCA_SCE | |
| 97 | USA_480VacHECO_14HO | |
| 98 | USA_208VacKAAI_14HO | |
| 99 | USA_240VacKAAI_14HO | |
| 100 | Australia B | AS/NZS 4777.2 |
| 101 | Australia C | AS/NZS 4777.2 |
| 102 | ChileMTA | |
| 103 | ChileMTB | |
| 104 | USA_208VacLUMA | |
| 105 | USA_240VacLUMA | |
| 106 | EN50549 | |

### Table 8-22 DRED

| DRED0 | DRED1 | DRED2 | DRED3 | DRED4 | DRED5 | DRED6 | DRED7 | DRED8 |
|---|---|---|---|---|---|---|---|---|
| 0x00FF | 0x0001 | 0x0002 | 0x0004 | 0x0008 | 0x0010 | 0x0020 | 0x0040 | 0x0080 |

### Table 8-23 Battery type index and BMS protocol (registers 27504, 27514)

| Battery type | Index / BMS protocol | Number of modules | Description |
|---|---|---|---|
| Lead Acid | 0x120 | NA | For debugging only; lead acid is not supported |
| DynessBMS | 0x130 | | |

### Table 8-24 Warning Code (register 174)

Chinese descriptions in the source are translated; the English identifier is as printed.

| Code | Identifier | Meaning (translated) |
|---|---|---|
| 0 | No warning | No warning |
| 1 | BatteryHardwareOverCurrent | Battery hardware overcurrent |
| 2 | BatteryBoostHardwareOverCurrent | Battery BOOST hardware overcurrent |
| 4 | DcCurrOutRangeSW | Battery BOOST software overcurrent or BMS overcurrent fault |
| 16 | BatteryCurrentRMSOverRange | Battery current RMS overcurrent |
| 64 | BatteryCurrentOverBMSRangeInOffGrid | Off-grid battery current exceeds BMS limit |
| 101 | PVBoostHardwareOverCurrent | PV BOOST hardware overcurrent |
| 102 | Utility Loss | Grid lost |
| 105 | Backup Overload | Load-side overload |
| 106 | Grid Overvoltage | Grid voltage sample too high |
| 107 | InvCurrOutRangeHW | Inverter hardware or software sampled overcurrent 8 times |
| 108 | PvOverCurrent | PV BOOST software overcurrent |
| 109 | Bus Overvoltage | BUS voltage too high |
| 120 | OffGridVoltageTooHigh | Off-grid output voltage too high |
| 121 | OffGridVoltageTooLow | Off-grid output voltage too low |
| 122 | BusVoltLow | BUS voltage too low |
| 123 | PvVoltLow | PV voltage too low |
| 125 | BatteryVoltageLowInOffGrid | Off-grid mode battery low-voltage shutdown protection |
| 126 | InvHardwareSingle-passCurrent | Inverter hardware single-pass overcurrent triggered |
| 128 | cBusSoftStartFail | Self-check BUS soft start failed |
| 129 | BatteryLossProtectNoPV | No-PV on-grid mode battery disconnect shutdown protection |
| 130 | Grid Backfilling | Grid backfeed |
| 131 | DSPSelfReset | DSP self-reset |
| 132 | cPVStatusChange | PV input state changed |
| 133 | Meter Failure | Meter failure under anti-backflow function |
| 134 | IslandHappen-PassiveMode | Islanding occurred (passive detection) |
| 135 | IslandHappen-ActiveMode | Islanding occurred (active detection) |
| 136 | EMSCommLoss | EMS communication lost |
| 137 | MicroElectricFault | Microelectronic fault |
| 140 | Force2WaitCommand | Received/responded to forced WAIT mode command |
| 141 | Force2StopCommand | Received/responded to forced stop command |
| 142 | Force2OffGridCommand | Received/responded to forced off-grid command |
| 150 | BypassRelayFaultOnGrid | Bypass relay closing fault in on-grid mode |
| 151 | BackupRelayFaultOffGrid | Load relay closing fault in off-grid mode |
| 152 | InvCurrUnbalance | Inverter current imbalance fault |
| 153 | CPLDWarning | CPLD fault |
| 154 | PLLWarning | PLL (phase lock) fault |
| 155 | Bus Unbalance | Bus unbalance |
| 156 | InvOutofControl | Inverter out of control |
| 157 | InvCurrOutRangeSW | Inverter software overcurrent |
| 158 | SoftCtrlShutdown | Restart-SPS command |
| 159 | System False | Re-tracking fault |
| 160 | InvCurrFalse | Inverter current fault |
| 161 | InvPwmFalse | PWM drive abnormal |
| 162 | OffGridPhaseFalse | Phase fault in off-grid mode |
| 163 | ModeFault | Module fault |
| 164 | EmsForceToWait | EMS shutdown fault |
| 165 | EmsStopMode | EMS stop mode |
| 166 | BatteryAbnormalConnect | Battery abnormally connected |
| 167 | BatteryAbnormalDisconnect | Battery abnormally disconnected |
| 168 | BmsCurrOutRangeSW | BMS software overcurrent |
| 169 | ModeFault2(MicroGridFault) | Microgrid fault |
| 170 | DSP-MasterWatchDogFault | Main DSP watchdog fault |
| 171 | NoBoxConnected | BOX not connected |
| 172 | TestTimerOccur | Test timer occurred |
| 173 | GridVFOutRange | Startup self-check: grid voltage/frequency out of limits |
| 174 | BusOverVoltageHW | Bus hardware overvoltage |
| 175 | InvL1OCHW | L1 inverter hardware overcurrent |
| 176 | InvL2OCHW | L2 inverter hardware overcurrent |
| 177 | InvL1constantOCHW | L1 inverter hardware sustained overcurrent |
| 178 | InvL2constantOCHW | L2 inverter hardware sustained overcurrent |
| 179 | Bat1OCHW | Battery 1 hardware overcurrent |
| 180 | Bat2OCHW | Battery 2 hardware overcurrent |
| 181 | Bus Inconsistent | Master/slave bus voltage inconsistent |
| 182 | OpenloopVoltFail | Open-loop self-check output voltage detection abnormal |
| 183 | OpenloopBuslow | Open-loop self-check bus voltage low |
| 184 | RelayCloseChkFail | Relay close-check abnormal |
| 185 | RelayOpenChkFail | Relay open-check abnormal |
| 200 | BatterySoftOverCurrent_S | Battery software overcurrent (slave DSP) |
| 202 | BatteryAbnormalConnect_S | Battery abnormally connected (slave DSP) |
| 203 | BatteryAbnormalDisconnect_S | Battery abnormally disconnected (slave DSP) |
| 204 | SyncFault_S | Slave DSP sync fault |
| 205 | DSP-SlaveWatchDogFault_S | Slave DSP watchdog fault |
| 206 | GridOverVoltAD_S | Grid voltage sample too high (slave DSP) |
| 207 | PvOverCurrAD_S | PV BOOST software overcurrent (slave DSP) |
| 208 | BusOverVoltAD_S | BUS voltage too high (slave DSP) |
| 209 | cBusVoltLow_S | BUS voltage too low (slave DSP) |
| 210 | cBusSoftStartFail_S | Self-check BUS soft start failed (slave DSP) |
| 211 | cPVStatusChange_S | PV input state changed (slave DSP) |
| 212 | MicroElectricFault | Microelectronic fault (slave DSP) |
| 213 | CANCommLoss_S | CAN communication lost (slave DSP) |
| 214 | PVBoostHardwareOverCurrent_S | PV Boost hardware overcurrent (slave DSP) |
| 215 | FwUpdateing_S | Firmware updating (slave DSP) |
| 216 | AirTempProbeFail_MS | Cavity (air) temperature probe abnormal |
| 217 | HtskTempProbeFail_MS | Heatsink temperature probe abnormal |
| 401 | Force2Wait | Forced wait |
| 402 | BMS Fail | BMS abnormal |
| 403 | ParallelCommLoss | Parallel communication abnormal |
| 404 | ParallelCabIDConflict | Parallel CabinetID conflict |
| 405 | ParallelNodeAbnormal | Abnormal number of parallel devices |
| 406 | ParallelExtCTLoss | Parallel external CT/MT not connected |
| 407 | BatteryActive | Battery activating |
| 408 | BatteryActivationFailure | Battery activation failed |
| 409 | OutOverLoad | Output overload |

---

## 7. CRC16

The PDF prints two 256-byte lookup tables (`auchCRCHi`, `auchCRCLo`) and the function `sCRC16`. They implement the standard **Modbus CRC-16** (initial value 0xFFFF, reflected polynomial 0xA001). The source text also quotes the polynomial as X^16 + X^12 + X^5 + 1 (the non-reflected CCITT form), but the lookup tables and the worked examples are standard Modbus CRC. The tables are not reproduced here; the equivalent bitwise implementation is:

```python
def modbus_crc16(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xA001 if crc & 1 else crc >> 1
    return crc

# On the wire the CRC is appended LOW byte first:
# frame = payload + bytes([crc & 0xFF, crc >> 8])
```

Verified against the document's examples (CRC low, high):

| Frame (without CRC) | CRC on wire |
|---|---|
| `01 03 00 01 00 02` | `95 CB` |
| `01 10 00 00 00 01 02 0A F0` | `A0 B4` |
| `01 10 00 00 00 01` (response) | `01 C9` |
| `01 06 00 00 0A F0` | `8F 2E` (the source labels these "high, low" in section 2.3, but the wire order is low = 8F, high = 2E) |

---

## Change record (translated)

| Ver. | Date | Modification |
|---|---|---|
| 1.00 | 2021-05-20 | Initial version |
| 1.01 | 2021-05-22 | Edit 4.2 Running Data Registers table |
| 1.02 | 2021-05-25 | Edit 4.2 table |
| 1.03 | 2021-05-27 | Edit 4.2 table |
| 1.04 | 2021-07-10 | Add running data register 213 BatterySOCValue |
| 1.05 | 2021-07-12 | 1. Adjust safety code Table 8-21. 2. Add 214 operate mode. 3. Rename 174 "work mode" to "work state". 4. Add bit2 BatBmsCommLoss and bit3 BackupFuncOn in 204 DiagStatusEx. 5. Modify 4.5 BMS information register address |
| 1.06 | 2021-07-14 | Modify 45224 PV E-Day from U32 to U16 |
| 1.07 | 2021-07-19 | Modify setting/control register addresses |
| 1.08 | 2021-08-13 | 1. Add 25522. 2. Modify 25443 |
| 1.09 | 2022-01-28 | Change register 2003 (battery temperature) to S16 |
| 1.10 | 2023-06-19 | 1. Rename register 25243 to OperationModeSet. 2. Rename register 25248 to ManageModeSet |
| 1.11 | 2023-07-18 | Power registers 120, 125, 130, 133, 135, 137, 143, 149, 155, 157, 159, 161 changed from S32 to S16; actual power = register value × power coefficient register |
| 1.11 | 2023-07-27 | Add two-phase three-wire grid type definition to register 2 |
| 1.12 | 2024-08-02 | 1. Adjust safety code table. 2. Adjust device-information register definitions |
| 1.13 | 2025-08-13 | 1. Complete RO data (full HT support). 2. Complete the 253xx segment data (full HT support). Prepared by Lingyang |
| 1.14 | 2026-04-23 | 1. Complete Table 8-24 Warning Code. 2. Complete Table 8-7 BMS Alarm Code |
| 1.15 | 2026-07-01 | 1. Add register 51, BMS version info. 2. Add 27547 and 27548 (source misprints "275448") for third-party EMS effective time and exit setting. 3. Register 27511: add mode 16 (battery charge-only self-use) |
| 1.15 | 2026-07-08 | Table 8-16: add code 0x0011 |

---

## Known inconsistencies in the source (for whoever consumes this file)

1. Power registers 120/125/130/133/135/137/143/149/155/157/159/161: change log says S16 × Power Ratio (reg 43); the register table still says S32 / 2 registers.
2. Register 274 `Vutility_T` is described as "S phase" (should be T).
3. Section 2 says CRC details are in "Chapter 10"; they are in section 7.
4. Change log references "45224", "2003", "4.5 BMS Information" and "275448", which do not match the current address layout (25224, 2003, section 4.3, 27548 respectively, by context).
5. Reg 25495 refers to Table 8-18 and Table 8-5/8-6/8-19 are missing; Table 8-12 is empty.
6. Register 25443 `GridFuncEnBitEE` and 25522 `GridFuncEnBit` are different registers.
7. Several 32-bit values (e.g. 177–180, 181–200 energy counters, 202–205) are documented as two separate "U32, 1 register" rows (`_L` / `_H`); treat each pair as one 32-bit value split into low word and high word registers.
