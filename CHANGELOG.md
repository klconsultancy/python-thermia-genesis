# Changelog

## [0.2.1](https://github.com/klconsultancy/python-thermia-genesis/compare/v0.2.0...v0.2.1) (2026-10-25)


### Bug Fixes

* accept every modbus-connection from 4.12.3 on ([#47](https://github.com/klconsultancy/python-thermia-genesis/issues/47)) ([c17df21](https://github.com/klconsultancy/python-thermia-genesis/commit/c17df21aa27d9dac1f23c052f6f110bd77ab365c))

## [0.2.0](https://github.com/klconsultancy/python-thermia-genesis/compare/v0.1.0...v0.2.0) (2026-10-25)


### Features

* cap the length of a read with max_block_size ([#44](https://github.com/klconsultancy/python-thermia-genesis/issues/44)) ([5c4a435](https://github.com/klconsultancy/python-thermia-genesis/commit/5c4a4359d4b810e1337931f61c040135f9cfd738))
* leave out the registers a pump refuses ([#46](https://github.com/klconsultancy/python-thermia-genesis/issues/46)) ([f8fc233](https://github.com/klconsultancy/python-thermia-genesis/commit/f8fc233efff3f1aa12a84bf9d1e11ea9c62e858d))

## 0.1.0 (2026-10-25)


### Features

* add 17.1 register map with consistency test ([#5](https://github.com/klconsultancy/python-thermia-genesis/issues/5)) ([0d33c96](https://github.com/klconsultancy/python-thermia-genesis/commit/0d33c96007f2839259b0fe3184b31dfb368d20d9))
* add the thermia-genesis dump command ([#29](https://github.com/klconsultancy/python-thermia-genesis/issues/29)) ([dfb224b](https://github.com/klconsultancy/python-thermia-genesis/commit/dfb224bc3ee5e39c709c477f85736f3f1b87914a))
* add the ThermiaGenesis API with async_update ([b24031c](https://github.com/klconsultancy/python-thermia-genesis/commit/b24031ce5a51b7926ba0ea8fe0fb6d68e7fc1943))
* detect the optional parts and read only what the pump has ([#27](https://github.com/klconsultancy/python-thermia-genesis/issues/27)) ([7504e25](https://github.com/klconsultancy/python-thermia-genesis/commit/7504e253b65ab4e98573b5ef317d160fee36f98c))
* expose the firmware version ([#28](https://github.com/klconsultancy/python-thermia-genesis/issues/28)) ([abc38cc](https://github.com/klconsultancy/python-thermia-genesis/commit/abc38cca41e84591cb671f249e8d9f03ff49274d))
* map the cooling registers of firmware 17.1 ([#22](https://github.com/klconsultancy/python-thermia-genesis/issues/22)) ([0809c97](https://github.com/klconsultancy/python-thermia-genesis/commit/0809c97eb932634f5e7b46a6f6f3106202f39f9d))
* map the electric meter registers of firmware 17.1 ([#24](https://github.com/klconsultancy/python-thermia-genesis/issues/24)) ([bf929ae](https://github.com/klconsultancy/python-thermia-genesis/commit/bf929ae5cf3b084715ec971a76d6f399618e2801))
* map the heat pump unit registers of firmware 17.1 ([#18](https://github.com/klconsultancy/python-thermia-genesis/issues/18)) ([ffd9923](https://github.com/klconsultancy/python-thermia-genesis/commit/ffd99230740e901d3c9d3318ceffd9287b0bdea3))
* map the heat registers of firmware 17.1 ([#20](https://github.com/klconsultancy/python-thermia-genesis/issues/20)) ([6c24ba5](https://github.com/klconsultancy/python-thermia-genesis/commit/6c24ba54996dde8889c5081095bfeff6dfcda452))
* map the pool registers of firmware 17.1 ([#23](https://github.com/klconsultancy/python-thermia-genesis/issues/23)) ([f3a1503](https://github.com/klconsultancy/python-thermia-genesis/commit/f3a15039144b42b1cbcee8fc7b0557f9f8e3cc28))
* map the status registers and complete the 17.1 map ([#25](https://github.com/klconsultancy/python-thermia-genesis/issues/25)) ([9abd506](https://github.com/klconsultancy/python-thermia-genesis/commit/9abd5062b6853c1663282f3e47aada52286c5649))
* map the tap water registers of firmware 17.1 ([#21](https://github.com/klconsultancy/python-thermia-genesis/issues/21)) ([badbbf5](https://github.com/klconsultancy/python-thermia-genesis/commit/badbbf53503eabc1750737d104c8390a59272b27))


### Bug Fixes

* read an absent room sensor as no value ([#40](https://github.com/klconsultancy/python-thermia-genesis/issues/40)) ([2d0dbee](https://github.com/klconsultancy/python-thermia-genesis/commit/2d0dbee54d8a2c1158ec4c5d73795a3a819d615e))
* read the cooling mix valve opening at scale 100 ([#41](https://github.com/klconsultancy/python-thermia-genesis/issues/41)) ([f3afa14](https://github.com/klconsultancy/python-thermia-genesis/commit/f3afa14601dc5bee6ade657ad73290d468a204d7))


### Documentation

* cite the 17.0 and Mega 17.1 documents in two errata rows ([#38](https://github.com/klconsultancy/python-thermia-genesis/issues/38)) ([065d06e](https://github.com/klconsultancy/python-thermia-genesis/commit/065d06eb59e0e6ef416e521d8b14286afca928e6))
* detect optional subsystems from their enable coils only ([#17](https://github.com/klconsultancy/python-thermia-genesis/issues/17)) ([d306b8d](https://github.com/klconsultancy/python-thermia-genesis/commit/d306b8deecf573ea39c8116aa733c31c61d903a8))
* record field confirmations in the errata ([#42](https://github.com/klconsultancy/python-thermia-genesis/issues/42)) ([f275a4a](https://github.com/klconsultancy/python-thermia-genesis/commit/f275a4a5961a283f081a3ef05eba29a2f77236b2))
* restore the negative number examples of chapter 2 ([#39](https://github.com/klconsultancy/python-thermia-genesis/issues/39)) ([8d6b655](https://github.com/klconsultancy/python-thermia-genesis/commit/8d6b65506ab22ff9d8b51d025e3aeb8d2ab9dc14))
