#include <ArduinoQueue.h>

ArduinoQueue<int> mission_steps(20);
void send_openMV_next_state(int curr_mision_step);
int curr_mission_step;
void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);
  Serial.setTimeout(200000);
}

void recieve_mission();

void loop() {
  // put your main code here, to run repeatedly:
  recieve_mission();
 /* delay(500);
  Serial.println(curr_mission_step);
  while(mission_steps.isEmpty())
  {
    curr_mission_step=mission_steps.dequeue();
    //send_openMV_next_state(curr_mission_step);
    Serial.println(curr_mission_step);
    delay(500);
  }*/
}

void recieve_mission()
{
  String s = Serial.readStringUntil('\n');
  Serial.println(s.length());
  unsigned int i=0;
  for(i=0;i<s.length();i++)
  { 
    mission_steps.enqueue(int(s[i]-'0'));
    Serial.println(s[i]);
  }
}
