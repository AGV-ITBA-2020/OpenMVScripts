
void setup() {
  // initialize both serial ports:
  Serial.begin(115200);
  Serial1.begin(38400);
}

void loop() {
  // read from port 1, send to port 0:
  String openMV_msg;
  openMV_msg=Serial1.readString();
  Serial.print(openMV_msg);
  //Serial1.print("abc!");
  Serial1.print("abc!");
}
