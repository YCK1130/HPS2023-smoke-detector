/*
Raspberry Pi LM75A IC2 temperature sample code.

Author: Leon Anavi <leon@anavi.org>

For more information and other samples for Raspberry Pi visit:
https://github.com/leon-anavi/rpi-examples

Circuit detail:
	Using CJMCU-75 (LM75A) Board Module
	VIN     - 	3.3V (Raspberry Pi pin 1)
	GND	    -	GND  (Raspberry Pi pin 14)
    SDA     -   SDA  (Raspberry Pi pin 3)
	SCL 	-	SCL  (Raspberry Pi pin 5)
	
	Note: Make sure LM75A is connected to 3.3V NOT the 5V pin!

Slave address:
	By default the application uses I2C address 0x48.
	Solder pins A0, A1 and A2 of LM75A to ground to use the default address.

	Otherwise, you can specify another address as a command line argument,
	for example: ./LM75A 0x4c
*/
#include <stdio.h>
#include <unistd.h>
#include <wiringPiI2C.h>

float getTemperature(int fd)
{
	int raw = wiringPiI2CReadReg16(fd, 0x00);
	raw = ((raw << 8) & 0xFF00) + (raw >> 8);
	return (float)((raw / 32.0) / 8.0);
}
 
int main(int argc, char *argv[]) 
{
	/* By default the address of LM75A is set to 0x48
	   aka A0, A1, and A2 are set to GND (0v). */
	int address = 0x48; int Keep_Run = 1;
	if (1 < argc)
	{
		address = (int)strtol(argv[1], NULL, 0);
	}

	/* Read from I2C and print temperature */
	if(Keep_Run){
		while(1){
			int fd = wiringPiI2CSetup(address);
			printf("%.2f\n", getTemperature(fd) );
			sleep(1);
		}
	}else{
		int fd = wiringPiI2CSetup(address);
		printf("%.2f\n", getTemperature(fd) );
	}

	return 0;

}
