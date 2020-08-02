byte openMV_msg;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial1.begin(38400);
  
  Serial1.setTimeout(20000);
  Serial.print("Waiting for OpenMV");
  while(!Serial1.available());
  openMV_msg=Serial1.read(); //Espero que se inicialice el openmv
  Serial1.write(0);
  Serial.print(openMV_msg);
  Serial.print("Connected");
}

void loop() {
  // put your main code here, to run repeatedly:
  while(!Serial1.available());

  openMV_msg=Serial1.read(); //Espero que se inicialice el openmv
  Serial.println(openMV_msg);

  
}
