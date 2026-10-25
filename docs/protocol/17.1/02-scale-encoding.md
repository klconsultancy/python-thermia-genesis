# 2 Scale, function, negative numbers & MSB/LSB

## 2.1 Scale, function, negative numbers & MSB/LSB

| Scale |                                                                       |
| ----- | --------------------------------------------------------------------- |
| 1     | No conversion factor                                                  |
| 10    | Conversion factor 10, i.e. the transmitted value is a tenfold larger  |
| 100   | Conversion factor 100, i.e. the transmitted value is a tenfold larger |

| Function | Function                          | Description                                     |
| -------- | --------------------------------- | ----------------------------------------------- |
| 1        | Read Coil Status                  | Read one or more consecutive boolean registers  |
| 2        | Read Input Status                 | Read one or more consecutive boolean registers  |
| 3        | Read Holding Registers            | Read one or more consecutive analog registers   |
| 4        | Read Input Registers              | Read one or more consecutive analog registers   |
| 5        | Force Single Coil                 | Write to one boolean register                   |
| 6        | Preset Single Holding Register    | Write to one analog register                    |
| 15       | Force Multiple Coils              | Write one or more consecutive boolean registers |
| 16       | Preset Multiple Holding Registers | Write one or more consecutive analog registers  |

### Negative numbers

Negative numbers are represented by the upper half of each 16 bit register.

```
100 = 100
...
2 = 2
1 = 1
0 = 0
-1 = 65535
-2 = 65534
-3 = 65533
...
-100 = 65436
etc.
```

Example: if "Brine out low alarm limit" register is set to -5 °C then, since the register has a scale of 100, the value read on Modbus should be 65036, representing -500.

Observe that not all variables are signed, i.e. "Compressor operating hours (LSB)" is a strict positive number between 0 to 65535.

### MSB/LSB

Some variables has potential to surpass their maximum value, for instance the variable "Compressor operating hours" can become larger than 65535.<br>
For these specific variables, that might be affected by this, there are two registers, MSB (Most Significant Bit) and LSB (Least Significant Bit) that can be combined in order to get a 32 bit number representation of the value.<br>
I.e. "Compressor operating hours" is separated in to "Compressor operating hours (MSB)" and "Compressor operating hours (LSB)". The LSB register is counting up by 1 for each hour that the compressor has been running and when it reaches 65535 then it will add 1 to the MSB register and reset the LSB register.<br>
In order to obtain the total Compressor operating hours then the two registers are combined into a 32 bit register where the MSB address represents the upper 16 bits and LSB represents the lower 16 bits.

Example:

```
Compressor operating hours (MSB) = 2
Compressor operating hours (LSB) = 2345
Total Compressor operating hours = 2 × 65536 (MSB) + 2345 (LSB) = 133417 hours
```

## 2.2 Addressing

A ’’De Facto-standard’’ have come to be with the purpose of simpler integration. Addressing is done as follows:

| First variable of | Is addressed | Typical function(s) |
| ----------------- | ------------ | ------------------- |
| COIL STATUS       | 00001        | 1, 5 (5=write)      |
| INPUT STATUS      | 10001        | 2                   |
| HOLDING REGISTERS | 40001        | 3, 6 (6=write)      |
| INPUT REGISTERS   | 30001        | 4                   |

Observe that some systems cannot handle aforementioned addressing system. Commonly a combination of function and absolute reference to 0 is used. The address table shows both alternatives.

## 2.3 Factory default

| Parameter   | Factory   | Range                                                                                                                                          |
| ----------- | --------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| Speed       | 19200 bps | 19200 (2400,4800,9600, 14400, 19200, 28800, 38400, 57600, 115200)                                                                              |
| Parity      | Even      | Even, none, odd                                                                                                                                |
| Address     | 1         | 1-247, not implemented on Modbus TCP/IP, the heat pump will respond to each address on its specific IPaddress using the designated modbus port |
| Start bit   | 1         | 1                                                                                                                                              |
| Stop bit    | 1         | 1 stop bit when Even or Odd Parity and optional when Parity None is chosen                                                                     |
| Data bit    | 8         | Data bits can only be 8 bits                                                                                                                   |
| Port        | 502       | 1-65535                                                                                                                                        |
| Modbus mode | RTU       | RTU, TCP/IP                                                                                                                                    |

## 2.4 Table key

| Reference to |                      |
| ------------ | -------------------- |
| 1            | Heating system       |
| 2            | Hot water            |
| 3            | TWC \*               |
| 4            | WCS \*               |
| 5            | Cooling              |
| 6            | Pool                 |
| 7            | Distribution circuit |
| 8            | Buffer tank          |
| 9            | Electric meter       |
| 10           | Internal heat pump   |

\* The reference number, does not apply to every heat pump model.
