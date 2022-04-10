#include "Arduino.h"
#include "ibus.h"

/*
 * See IbusReader.cs for details about the IBUS protocol
 */

//#define KEY 0x40 // this is given through begin()#define SIZEANDKEY 2 //bytes#define CHECKSUMSIZE 2

IBus::IBus(int numChannels) {
  //dataSent = DATASIZE + numChannels*2 + CHECKSUMSIZE;  dataSent = SIZEANDKEY + numChannels*2 + CHECKSUMSIZE;
}

void IBus::begin(byte Key) {
  checksum = 0xffff - dataSent - Key;
  Serial.write(dataSent);
  Serial.write(Key);
}

void IBus::end() {
  // write checksum
  Serial.write(checksum & 0xff);
  Serial.write(checksum >> 8);
}

/*
 * Write 16bit value in little endian format and update checksum
 */
void IBus::write(unsigned short val) {
  byte b = val & 0xff;
  Serial.write(b);
  checksum -= b;
  b = val >> 8;
  Serial.write(b);
  checksum -= b;
}
