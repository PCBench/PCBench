EESchema Schematic File Version 4
EELAYER 30 0
EELAYER END
$Descr User 11701 8846
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
Wire Wire Line
	4100 4500 4100 4000
Wire Wire Line
	4100 4000 4100 3900
Wire Wire Line
	4100 3900 4300 3900
Wire Wire Line
	4300 4000 4100 4000
Connection ~ 4100 4000
Text Label 4100 4500 0    10   ~ 0
GND
Wire Wire Line
	5500 4500 5500 4400
Text Label 5500 4500 0    10   ~ 0
GND
Wire Wire Line
	2400 7100 4500 7100
Wire Wire Line
	4500 7100 4500 7300
Wire Wire Line
	4500 7300 4500 7400
Wire Wire Line
	4600 7300 4500 7300
Connection ~ 4500 7300
Text Label 2400 7100 0    10   ~ 0
GND
Wire Wire Line
	4700 2900 4700 2700
Text Label 4700 2900 0    10   ~ 0
GND
Wire Wire Line
	3800 4500 3800 4400
Text Label 3800 4500 0    10   ~ 0
GND
Wire Wire Line
	3600 3000 3600 2900
Text Label 3600 3000 0    10   ~ 0
GND
Wire Wire Line
	3300 2700 3300 2600
Text Label 3300 2700 0    10   ~ 0
GND
Wire Wire Line
	5500 4100 5500 4000
Wire Wire Line
	6000 4000 5500 4000
Wire Wire Line
	5500 4000 5300 4000
Connection ~ 5500 4000
Wire Wire Line
	5300 3500 5500 3500
Text Label 5500 3500 0    50   ~ 0
SCL
Wire Wire Line
	2400 6800 3300 6800
Wire Wire Line
	3300 6800 4100 6800
Wire Wire Line
	3300 6700 3300 6800
Text Label 4100 6800 0    50   ~ 0
SCL
Connection ~ 3300 6800
Wire Wire Line
	5300 3400 5500 3400
Text Label 5500 3400 0    50   ~ 0
SDA
Wire Wire Line
	2400 6900 3900 6900
Wire Wire Line
	3900 6900 4100 6900
Wire Wire Line
	3900 6700 3900 6900
Text Label 4100 6900 0    50   ~ 0
SDA
Connection ~ 3900 6900
Wire Wire Line
	5300 3600 6000 3600
Wire Wire Line
	6000 3600 6000 3400
Text Label 6000 3400 0    50   ~ 0
CS
Wire Wire Line
	2400 6600 2600 6600
Text Label 2600 6600 0    50   ~ 0
CS
Wire Wire Line
	4300 3400 4100 3400
Wire Wire Line
	4100 3400 4100 2500
Wire Wire Line
	4100 2500 4500 2500
Text Label 4100 2500 0    50   ~ 0
SDO/SA0
Wire Wire Line
	2400 6700 2600 6700
Text Label 2600 6700 0    50   ~ 0
SDO/SA0
Wire Wire Line
	4300 3500 4000 3500
Wire Wire Line
	4000 3500 4000 2000
Wire Wire Line
	3300 2200 3300 2000
Wire Wire Line
	3300 2000 4000 2000
Text Label 3300 2000 0    50   ~ 0
SDX
Wire Wire Line
	6100 6800 6200 6800
Text Label 6200 6800 0    50   ~ 0
SDX
Wire Wire Line
	4300 3600 3900 3600
Wire Wire Line
	3900 3600 3900 2400
Wire Wire Line
	3600 2500 3600 2400
Wire Wire Line
	3600 2400 3900 2400
Text Label 3600 2450 0    50   ~ 0
SCX
Wire Wire Line
	6100 6700 6200 6700
Text Label 6200 6700 0    50   ~ 0
SCX
Wire Wire Line
	4100 3700 4300 3700
Text Label 4100 3700 2    50   ~ 0
INT1
Wire Wire Line
	6100 6500 6200 6500
Text Label 6200 6500 0    50   ~ 0
INT1
Wire Wire Line
	5300 3900 5500 3900
Text Label 5500 3900 0    50   ~ 0
INT2
Wire Wire Line
	6100 6400 6200 6400
Text Label 6200 6400 0    50   ~ 0
INT2
Wire Wire Line
	4700 2100 4700 2300
Text Label 4700 2100 0    10   ~ 0
3.3V
Wire Wire Line
	3600 3800 3600 3700
Wire Wire Line
	4300 3800 3800 3800
Wire Wire Line
	3800 3800 3600 3800
Wire Wire Line
	3800 4100 3800 3800
Connection ~ 3800 3800
Text Label 3600 3800 0    10   ~ 0
3.3V
Wire Wire Line
	7600 4000 7600 3700
Wire Wire Line
	6600 4000 7600 4000
Text Label 7600 4000 0    10   ~ 0
3.3V
Wire Wire Line
	2400 7000 4500 7000
Wire Wire Line
	4500 7000 4500 6800
Wire Wire Line
	4500 6800 4500 6500
Wire Wire Line
	4600 6800 4500 6800
Connection ~ 4500 6800
Text Label 2400 7000 0    10   ~ 0
3.3V
Wire Wire Line
	6000 2700 6000 3000
Text Label 6000 2700 0    10   ~ 0
3.3V
Wire Wire Line
	3600 5900 3600 6000
Text Label 3600 5900 0    10   ~ 0
3.3V
Wire Wire Line
	5300 3800 5500 3800
Text Label 5500 3800 0    50   ~ 0
OCS
Wire Wire Line
	6100 6600 6200 6600
Text Label 6200 6600 0    50   ~ 0
OCS
Wire Wire Line
	3300 6300 3300 6200
Wire Wire Line
	3300 6200 3400 6200
Wire Wire Line
	3800 6200 3900 6200
Wire Wire Line
	3900 6200 3900 6300
$Comp
L LSM6DS3_Breakout-eagle-import:FRAME-LETTER FRAME1
U 1 1 CC96BE83
P 1100 8000
F 0 "FRAME1" H 1100 8000 50  0001 C CNN
F 1 "FRAME-LETTER" H 1100 8000 50  0001 C CNN
F 2 "LSM6DS3_Breakout:CREATIVE_COMMONS" H 1100 8000 50  0001 C CNN
F 3 "" H 1100 8000 50  0001 C CNN
F 4 "Marshall Taylor" H 1100 8000 50  0001 C CNN "DESIGNER"
F 5 "v10" H 1100 8000 50  0001 C CNN "VERSION"
	1    1100 8000
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:FRAME-LETTER FRAME1
U 2 1 CC96BE8F
P 6900 8000
F 0 "FRAME1" H 6900 8000 50  0001 C CNN
F 1 "FRAME-LETTER" H 6900 8000 50  0001 C CNN
F 2 "LSM6DS3_Breakout:CREATIVE_COMMONS" H 6900 8000 50  0001 C CNN
F 3 "" H 6900 8000 50  0001 C CNN
F 4 "Marshall Taylor" H 7880 8450 50  0001 L BNN "DESIGNER"
F 5 "v10" H 10400 8250 50  0001 L BNN "VERSION"
	2    6900 8000
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:LSM6DS3DOT_INDICATION U2
U 1 1 9FF179F9
P 4800 3700
F 0 "U2" H 5030 3200 70  0000 L BNN
F 1 "LSM6DS3" H 4540 4130 70  0000 L BNN
F 2 "LSM6DS3_Breakout:LGA14L_DOT_INDICATOR" H 4800 3700 50  0001 C CNN
F 3 "" H 4800 3700 50  0001 C CNN
	1    4800 3700
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:GND #GND04
U 1 1 12C122FD
P 4100 4600
F 0 "#GND04" H 4100 4600 50  0001 C CNN
F 1 "GND" H 4000 4500 59  0000 L BNN
F 2 "" H 4100 4600 50  0001 C CNN
F 3 "" H 4100 4600 50  0001 C CNN
	1    4100 4600
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:3.3V #SUPPLY04
U 1 1 1C9152C2
P 3600 3700
F 0 "#SUPPLY04" H 3600 3700 50  0001 C CNN
F 1 "3.3V" H 3560 3840 59  0000 L BNN
F 2 "" H 3600 3700 50  0001 C CNN
F 3 "" H 3600 3700 50  0001 C CNN
	1    3600 3700
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:3.3V #SUPPLY05
U 1 1 20B1DDDE
P 7600 3700
F 0 "#SUPPLY05" H 7600 3700 50  0001 C CNN
F 1 "3.3V" H 7560 3840 59  0000 L BNN
F 2 "" H 7600 3700 50  0001 C CNN
F 3 "" H 7600 3700 50  0001 C CNN
	1    7600 3700
	-1   0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:GND #GND05
U 1 1 5B6A58CA
P 5500 4600
F 0 "#GND05" H 5500 4600 50  0001 C CNN
F 1 "GND" H 5400 4500 59  0000 L BNN
F 2 "" H 5500 4600 50  0001 C CNN
F 3 "" H 5500 4600 50  0001 C CNN
	1    5500 4600
	-1   0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:0.1UF-100V-10%(0603) C3
U 1 1 88676885
P 5500 4300
F 0 "C3" H 5560 4415 59  0000 L BNN
F 1 "0.1uF" H 5560 4215 59  0000 L BNN
F 2 "LSM6DS3_Breakout:0603-CAP" H 5500 4300 50  0001 C CNN
F 3 "" H 5500 4300 50  0001 C CNN
	1    5500 4300
	-1   0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:JUMPER-PAD-3-2OF3_NC_BY_PASTE SJ1
U 1 1 666E743F
P 4700 2500
F 0 "SJ1" H 4800 2515 59  0000 L BNN
F 1 "JUMPER-PAD-3-2OF3_NC_BY_PASTE" H 4800 2425 59  0000 L BNN
F 2 "LSM6DS3_Breakout:PAD-JUMPER-3-2OF3_NC_BY_PASTE_YES_SILK_FULL_BOX" H 4700 2500 50  0001 C CNN
F 3 "" H 4700 2500 50  0001 C CNN
	1    4700 2500
	1    0    0    1   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:GND #GND06
U 1 1 F6847280
P 4700 3000
F 0 "#GND06" H 4700 3000 50  0001 C CNN
F 1 "GND" H 4600 2900 59  0000 L BNN
F 2 "" H 4700 3000 50  0001 C CNN
F 3 "" H 4700 3000 50  0001 C CNN
	1    4700 3000
	-1   0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:3.3V #SUPPLY010
U 1 1 28999800
P 4700 2100
F 0 "#SUPPLY010" H 4700 2100 50  0001 C CNN
F 1 "3.3V" H 4660 2240 59  0000 L BNN
F 2 "" H 4700 2100 50  0001 C CNN
F 3 "" H 4700 2100 50  0001 C CNN
	1    4700 2100
	-1   0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:3.3V #SUPPLY011
U 1 1 E0B04C0E
P 6000 2700
F 0 "#SUPPLY011" H 6000 2700 50  0001 C CNN
F 1 "3.3V" H 5960 2840 59  0000 L BNN
F 2 "" H 6000 2700 50  0001 C CNN
F 3 "" H 6000 2700 50  0001 C CNN
	1    6000 2700
	-1   0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:0.1UF-100V-10%(0603) C4
U 1 1 03F6E73E
P 3800 4300
F 0 "C4" H 3860 4415 59  0000 L BNN
F 1 "0.1uF" H 3860 4215 59  0000 L BNN
F 2 "LSM6DS3_Breakout:0603-CAP" H 3800 4300 50  0001 C CNN
F 3 "" H 3800 4300 50  0001 C CNN
	1    3800 4300
	-1   0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:GND #GND010
U 1 1 0087CD10
P 3800 4600
F 0 "#GND010" H 3800 4600 50  0001 C CNN
F 1 "GND" H 3700 4500 59  0000 L BNN
F 2 "" H 3800 4600 50  0001 C CNN
F 3 "" H 3800 4600 50  0001 C CNN
	1    3800 4600
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:SFE_LOGO_FLAME.2_INCH LOGO1
U 1 1 6FA33304
P 9410 6280
F 0 "LOGO1" H 9410 6280 50  0001 C CNN
F 1 "SFE_LOGO_FLAME.2_INCH" H 9410 6280 50  0001 C CNN
F 2 "LSM6DS3_Breakout:SFE_LOGO_FLAME_.2" H 9410 6280 50  0001 C CNN
F 3 "" H 9410 6280 50  0001 C CNN
	1    9410 6280
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:OSHW-LOGOS LOGO2
U 1 1 6CBFEB06
P 10330 5980
F 0 "LOGO2" H 10330 5980 50  0001 C CNN
F 1 "OSHW-LOGOS" H 10330 5980 50  0001 C CNN
F 2 "LSM6DS3_Breakout:OSHW-LOGO-S" H 10330 5980 50  0001 C CNN
F 3 "" H 10330 5980 50  0001 C CNN
	1    10330 5980
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:STAND-OFF STANDOFF1
U 1 1 8BDC6CF5
P 7100 5500
F 0 "STANDOFF1" H 7100 5500 50  0001 C CNN
F 1 "STAND-OFF" H 7100 5500 50  0001 C CNN
F 2 "LSM6DS3_Breakout:STAND-OFF" H 7100 5500 50  0001 C CNN
F 3 "" H 7100 5500 50  0001 C CNN
	1    7100 5500
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:STAND-OFF STANDOFF2
U 1 1 B412F2A4
P 7300 5500
F 0 "STANDOFF2" H 7300 5500 50  0001 C CNN
F 1 "STAND-OFF" H 7300 5500 50  0001 C CNN
F 2 "LSM6DS3_Breakout:STAND-OFF" H 7300 5500 50  0001 C CNN
F 3 "" H 7300 5500 50  0001 C CNN
	1    7300 5500
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:STAND-OFF STANDOFF3
U 1 1 AA2E56E5
P 7500 5500
F 0 "STANDOFF3" H 7500 5500 50  0001 C CNN
F 1 "STAND-OFF" H 7500 5500 50  0001 C CNN
F 2 "LSM6DS3_Breakout:STAND-OFF" H 7500 5500 50  0001 C CNN
F 3 "" H 7500 5500 50  0001 C CNN
	1    7500 5500
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:STAND-OFF STANDOFF4
U 1 1 76634FB5
P 7700 5500
F 0 "STANDOFF4" H 7700 5500 50  0001 C CNN
F 1 "STAND-OFF" H 7700 5500 50  0001 C CNN
F 2 "LSM6DS3_Breakout:STAND-OFF" H 7700 5500 50  0001 C CNN
F 3 "" H 7700 5500 50  0001 C CNN
	1    7700 5500
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:4.7KOHM-1_10W-1%(0603) R1
U 1 1 9D727F8A
P 3300 6500
F 0 "R1" H 3150 6559 59  0000 L BNN
F 1 "4.7K" H 3150 6370 59  0000 L BNN
F 2 "LSM6DS3_Breakout:0603-RES" H 3300 6500 50  0001 C CNN
F 3 "" H 3300 6500 50  0001 C CNN
	1    3300 6500
	0    -1   -1   0   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:4.7KOHM-1_10W-1%(0603) R2
U 1 1 4C4A9837
P 3900 6500
F 0 "R2" H 3750 6559 59  0000 L BNN
F 1 "4.7K" H 3750 6370 59  0000 L BNN
F 2 "LSM6DS3_Breakout:0603-RES" H 3900 6500 50  0001 C CNN
F 3 "" H 3900 6500 50  0001 C CNN
	1    3900 6500
	0    -1   -1   0   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:3.3V #SUPPLY02
U 1 1 19032892
P 3600 5900
F 0 "#SUPPLY02" H 3600 5900 50  0001 C CNN
F 1 "3.3V" H 3560 6040 59  0000 L BNN
F 2 "" H 3600 5900 50  0001 C CNN
F 3 "" H 3600 5900 50  0001 C CNN
	1    3600 5900
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:INDUCTOR30OHM,1.8A L1
U 1 1 23FDA8DF
P 6300 4000
F 0 "L1" V 6450 3860 59  0000 L BNN
F 1 "RES-07859" V 6550 3860 59  0000 L BNN
F 2 "LSM6DS3_Breakout:0603" H 6300 4000 50  0001 C CNN
F 3 "" H 6300 4000 50  0001 C CNN
	1    6300 4000
	0    1    1    0   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:FIDUCIAL1X2 FID1
U 1 1 57AF2ED6
P 7100 5700
F 0 "FID1" H 7100 5700 50  0001 C CNN
F 1 "FIDUCIAL1X2" H 7100 5700 50  0001 C CNN
F 2 "LSM6DS3_Breakout:FIDUCIAL-1X2" H 7100 5700 50  0001 C CNN
F 3 "" H 7100 5700 50  0001 C CNN
	1    7100 5700
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:FIDUCIAL1X2 FID2
U 1 1 AD69ACBC
P 7300 5700
F 0 "FID2" H 7300 5700 50  0001 C CNN
F 1 "FIDUCIAL1X2" H 7300 5700 50  0001 C CNN
F 2 "LSM6DS3_Breakout:FIDUCIAL-1X2" H 7300 5700 50  0001 C CNN
F 3 "" H 7300 5700 50  0001 C CNN
	1    7300 5700
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:3.3V #SUPPLY06
U 1 1 A7CD5EB6
P 4500 6500
F 0 "#SUPPLY06" H 4500 6500 50  0001 C CNN
F 1 "3.3V" H 4460 6640 59  0000 L BNN
F 2 "" H 4500 6500 50  0001 C CNN
F 3 "" H 4500 6500 50  0001 C CNN
	1    4500 6500
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:GND #GND011
U 1 1 5518330F
P 4500 7500
F 0 "#GND011" H 4500 7500 50  0001 C CNN
F 1 "GND" H 4400 7400 59  0000 L BNN
F 2 "" H 4500 7500 50  0001 C CNN
F 3 "" H 4500 7500 50  0001 C CNN
	1    4500 7500
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:10KOHM-1_10W-1%(0603)0603 R3
U 1 1 2A684572
P 6000 3200
F 0 "R3" H 5850 3259 59  0000 L BNN
F 1 "10K" H 5850 3070 59  0000 L BNN
F 2 "LSM6DS3_Breakout:0603-RES" H 6000 3200 50  0001 C CNN
F 3 "" H 6000 3200 50  0001 C CNN
	1    6000 3200
	0    -1   -1   0   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:JUMPER-PAD-3-NC_BY_TRACE SJ2
U 1 1 0D387D6A
P 3600 6200
F 0 "SJ2" H 3700 6215 59  0000 L BNN
F 1 "S_MODE" H 3700 6125 59  0000 L BNN
F 2 "LSM6DS3_Breakout:PAD-JUMPER-3-3OF3_NC_BY_TRACE_YES_SILK_FULL_BOX" H 3600 6200 50  0001 C CNN
F 3 "" H 3600 6200 50  0001 C CNN
	1    3600 6200
	0    -1   1    0   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:M06NO_SILK_YES_STOP JP1
U 1 1 62378055
P 2200 6800
F 0 "JP1" H 2000 7230 59  0000 L BNN
F 1 "IO" H 2000 6400 59  0000 L BNN
F 2 "LSM6DS3_Breakout:1X06_NO_SILK_YES_STOP" H 2200 6800 50  0001 C CNN
F 3 "" H 2200 6800 50  0001 C CNN
	1    2200 6800
	1    0    0    1   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:GND #GND01
U 1 1 8DA2BB24
P 3300 2800
F 0 "#GND01" H 3300 2800 50  0001 C CNN
F 1 "GND" H 3200 2700 59  0000 L BNN
F 2 "" H 3300 2800 50  0001 C CNN
F 3 "" H 3300 2800 50  0001 C CNN
	1    3300 2800
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:GND #GND02
U 1 1 4877C9E2
P 3600 3100
F 0 "#GND02" H 3600 3100 50  0001 C CNN
F 1 "GND" H 3500 3000 59  0000 L BNN
F 2 "" H 3600 3100 50  0001 C CNN
F 3 "" H 3600 3100 50  0001 C CNN
	1    3600 3100
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:JUMPER-PAD-2-NC_BY_TRACE SJ3
U 1 1 787D351D
P 3300 2400
F 0 "SJ3" H 3200 2500 59  0000 L BNN
F 1 "JUMPER-PAD-2-NC_BY_TRACE" H 3200 2200 59  0001 L BNN
F 2 "LSM6DS3_Breakout:PAD-JUMPER-2-NC_BY_TRACE_YES_SILK" H 3300 2400 50  0001 C CNN
F 3 "" H 3300 2400 50  0001 C CNN
	1    3300 2400
	0    -1   -1   0   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:JUMPER-PAD-2-NC_BY_TRACE SJ4
U 1 1 CDD69D21
P 3600 2700
F 0 "SJ4" H 3500 2800 59  0000 L BNN
F 1 "JUMPER-PAD-2-NC_BY_TRACE" H 3500 2500 59  0001 L BNN
F 2 "LSM6DS3_Breakout:PAD-JUMPER-2-NC_BY_TRACE_YES_SILK" H 3600 2700 50  0001 C CNN
F 3 "" H 3600 2700 50  0001 C CNN
	1    3600 2700
	0    -1   -1   0   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:M01PTH_NO_SILK_YES_STOP JP2
U 1 1 0F7FE282
P 4900 6800
F 0 "JP2" H 4800 6930 59  0000 L BNN
F 1 "3.3V" H 4800 6600 59  0000 L BNN
F 2 "LSM6DS3_Breakout:1X01_NO_SILK" H 4900 6800 50  0001 C CNN
F 3 "" H 4900 6800 50  0001 C CNN
	1    4900 6800
	-1   0    0    1   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:M01PTH_NO_SILK_YES_STOP JP11
U 1 1 07C5E5FF
P 4900 7300
F 0 "JP11" H 4800 7430 59  0000 L BNN
F 1 "GND" H 4800 7100 59  0000 L BNN
F 2 "LSM6DS3_Breakout:1X01_NO_SILK" H 4900 7300 50  0001 C CNN
F 3 "" H 4900 7300 50  0001 C CNN
	1    4900 7300
	-1   0    0    1   
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:SFE_LOGO_NAME_FLAME.1_INCH LOGO3
U 1 1 73894340
P 7000 6500
F 0 "LOGO3" H 7000 6500 50  0001 C CNN
F 1 "SFE_LOGO_NAME_FLAME.1_INCH" H 7000 6500 50  0001 C CNN
F 2 "LSM6DS3_Breakout:SFE_LOGO_NAME_FLAME_.1" H 7000 6500 50  0001 C CNN
F 3 "" H 7000 6500 50  0001 C CNN
	1    7000 6500
	1    0    0    -1  
$EndComp
$Comp
L LSM6DS3_Breakout-eagle-import:M05PTH JP3
U 1 1 E8D5A2E6
P 5800 6600
F 0 "JP3" H 5700 6930 59  0000 L BNN
F 1 "IO" H 5700 6200 59  0000 L BNN
F 2 "LSM6DS3_Breakout:1X05" H 5800 6600 50  0001 C CNN
F 3 "" H 5800 6600 50  0001 C CNN
	1    5800 6600
	1    0    0    1   
$EndComp
Wire Notes Line
	6900 6600 6900 5300
Text Notes 4920 1830 0    59   ~ 0
SJ1 controls the lowest bit\nof the I2C address.
Text Notes 1400 1100 0    127  ~ 0
LSM6DS3
Text Notes 3180 2870 0    59   ~ 0
If downstream SPI devices are\nhosted by the LSM6DS3, release\nSCx and SDx from ground by\nopening SJ3 and SJ4.
Text Notes 4920 2080 0    59   ~ 0
Address can be:\n1101011b (0x6B)\n1101010b (0x6A)
Text Notes 3640 5920 0    59   ~ 0
Enable pull-up resistors\nfor I2C operation
Text Notes 7800 1200 0    59   ~ 0
SERIAL MODES\nMODE1:  Slave-only mode\n   I2C or SPI\nMODE2:  Sensor Hub mode\n   I2C or SPI with master I2C port\nMODE3:  AUX SPI mode\n   I2C and SPI access (Multi-read)   
Wire Notes Line
	1100 5300 10900 5300
$EndSCHEMATC
