# Bus Definition
This folder contains the Neware RS485 Bus Protocol Definition in a TOML file, and the python script necessary to generate ```api/rs485``` from the TOML file.

## Bus Definition TOML File
The ```toml``` file contains everything needed to describe the Neware RS485 Protocol. It includes parameters like bus speed and UART configuration, to the layout of individual messages. When new messages reverse engineered and added to the protocol, they are added to this TOML file.

## API Autogenerator
The API autogenerator reads the ```toml``` and produces all of the code in ```api/rs485```. This allows to API code to remain easy to interface with and descriptive, while allowing the bus protocol definition in the TOML file to be concise and easily updatable. This autogenerator is written in Python for easy string manipulation. The autogenerator could feasibly be updated in the future to produce an API in any language such as rust, C, or others. For now, the API is generated in Python to allow for easy readability and wide compatibility across devices and operating systems.