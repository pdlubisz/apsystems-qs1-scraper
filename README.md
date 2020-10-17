# What is this

This code is meant to download information from APSystems ECU (Energy Communiction Unit)
and send it to pvoutput.org

## How to install

1. Clone the code
2. Install venv 
3. install requirements
4. Prepare `config.ini` based on `example-config.ini`

## How to run it

Just run `exporttopvoutput.sh`

## What it does

The code will connect to ECU (make sure to put the right IP in `config.ini`),
grab current power, daily generation and other 
(basically it grabs everything from the table on the home page)

When we have the data it will send it to pvoutput.org - make sure you provide apikey to your account.

