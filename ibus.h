#pragma once

class IBus {
  private:
    int dataSent;
    int checksum;
  public:
    IBus(int numChannels);
  
    void begin(byte Key);
    void end();
    void write(unsigned short);
    
};

