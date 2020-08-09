#include <ArduinoQueue.h>
#define OPEN_MV_MSG_LEN 2 //Length en bytes
#define ON_BOARD_LED_PIN 13
#define MAX_DISPLACEMENT 64


typedef enum {OPENMV_FOLLOW_LINE, OPENMV_FORK_LEFT, OPENMV_FORK_RIGHT, OPENMV_MERGE, OPENMV_ERROR,OPENMV_IDLE}openMV_states; //Los distintos estados del OpenMV
typedef enum {MISSION_SLOW_DOWN, MISSION_SPEED_UP, MISSION_FORK_LEFT, MISSION_FORK_RIGHT, MISSION_STATION, WAIT_FOR_MISSION}Mission_states; //Los distintos objetivos de la mision
typedef struct  {
  int displacement;
  bool tag_found;
  bool form_passed;
  bool error;
  String tag;
}openMV_msg; //La información que trae cada mensaje del openMV.

openMV_msg decode_openMV_msg(byte *openMV_msg_buff);
ArduinoQueue<int> Mission(20); //Máximo 20 pasos de misiones 
void answer(openMV_msg msg);
int curr_mission_step;
void send_openMV_next_state(int urr_mision_step);
void print_openmv_msg(openMV_msg msg);

void setup() {
  // initialize both serial ports:
  Serial.begin(115200);
  Serial1.begin(38400);
  byte openMV_msg;
  Serial1.setTimeout(20000);
  Serial.print("Waiting for OpenMV");
  while(!Serial1.available());
  openMV_msg=Serial1.read(); //Espero que se inicialice el openmv
  Serial1.write(OPENMV_FOLLOW_LINE);
  Serial.println(openMV_msg);
  Serial.println("Connected");
  
  Mission.enqueue(MISSION_SLOW_DOWN);  //La mision que le hardcodeamos.
  Mission.enqueue(MISSION_FORK_LEFT);
  Mission.enqueue(MISSION_STATION);

  curr_mission_step=Mission.dequeue();
  
  pinMode(ON_BOARD_LED_PIN,OUTPUT); //Puedo usar el LED para indicar que tan desplazado está.
}

void loop() {
  // read from port 1, send to port 0:
  if(Serial1.available())
  {
    byte openMV_msg_buff[OPEN_MV_MSG_LEN];
    openMV_msg_buff[0] = Serial1.read(); //Esto estaría bueno en la CIAA implementar una interrupción cuando recibe 2 mensajes.
    while(!Serial1.available());
    openMV_msg_buff[1] = Serial1.read();
    openMV_msg msg = decode_openMV_msg(openMV_msg_buff);
    //Serial.print(openMV_msg_buff[0],BIN); //Vista ultra Raw de los mensajes.
    //Serial.print(openMV_msg_buff[1],BIN); //Vista ultra Raw de los mensajes.
    //Serial.println(openMV_msg_buff[0],openMV_msg_buff[1]); //Vista Raw de los mensajes.
    print_openmv_msg(msg);
    //Serial.print("Desplazamiento");
    //Serial.println(msg.displacement);
    analogWrite(ON_BOARD_LED_PIN,int(abs(msg.displacement)*255/MAX_DISPLACEMENT));
    answer(msg);
  }
}

void print_openmv_msg(openMV_msg msg)
{ 
  Serial.print("Desplazamiento :");
  Serial.print(msg.displacement);
  Serial.print(", err :");
  Serial.print(msg.error);
  Serial.print(",form passed:");
  Serial.print(msg.form_passed);
  Serial.print(", tag found :");
  Serial.print(msg.tag_found);
  Serial.print(", tag :");
  Serial.println(msg.tag);
}

openMV_msg decode_openMV_msg(byte *openMV_msg_buff)
{
  openMV_msg retVal;
  retVal.displacement=int(char(openMV_msg_buff[0]));
  retVal.error= (openMV_msg_buff[1] /128)%2;
  retVal.form_passed= (openMV_msg_buff[1]/64)%2;
  retVal.tag_found= (openMV_msg_buff[1]/32)%2;
  unsigned int tag_nmbr=openMV_msg_buff[1]%32;
  if (tag_nmbr == 1)
    retVal.tag = "Slow down tag";
  else if (tag_nmbr == 3)
    retVal.tag = "Station tag";
  else
    retVal.tag = "None";
  return retVal;
}
void answer(openMV_msg msg)
{
  
  if (curr_mission_step != WAIT_FOR_MISSION) //Si todavía quedan partes de la misión
  {
    /*if ( msg.error == 1)
    {
      unsigned int items= Mission.itemCount();
      for(unsigned int i=0; i<items;i++);
        Mission.dequeue();
      Serial1.write(OPENMV_FOLLOW_LINE); // Estado normal
      curr_mission_step=WAIT_FOR_MISSION;
    }
    else*/ if ((curr_mission_step == MISSION_SLOW_DOWN) && msg.tag_found && msg.tag=="Slow down tag")
    {
      curr_mission_step=Mission.dequeue();
      send_openMV_next_state(curr_mission_step);
    }
    else if ((curr_mission_step == MISSION_FORK_LEFT) && msg.form_passed)
    {
      curr_mission_step=Mission.dequeue();
      send_openMV_next_state(curr_mission_step);
    }
    else if ((curr_mission_step == MISSION_STATION) && msg.tag_found && msg.tag=="Station tag")
    {
      if(Mission.isEmpty())
        curr_mission_step = WAIT_FOR_MISSION;
      else
        curr_mission_step=Mission.dequeue();
      send_openMV_next_state(curr_mission_step);
    }
  }
}

void send_openMV_next_state(int curr_mision_step)
{ //Faltan poner más estados
  if(curr_mision_step == MISSION_FORK_LEFT)
    Serial1.write(OPENMV_FORK_LEFT);
  else if(curr_mision_step == MISSION_FORK_RIGHT)
    Serial1.write(OPENMV_FORK_RIGHT);
  else if(curr_mision_step == MISSION_STATION)
    Serial1.write(OPENMV_FOLLOW_LINE);
  else if(curr_mision_step == WAIT_FOR_MISSION)
    Serial1.write(OPENMV_IDLE);
}
