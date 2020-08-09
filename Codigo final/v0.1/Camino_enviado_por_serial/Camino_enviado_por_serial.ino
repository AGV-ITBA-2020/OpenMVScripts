#include <ArduinoQueue.h>
#define OPEN_MV_MSG_LEN 2 //Length en bytes
#define ON_BOARD_LED_PIN 13 //Para mostrar cosas
#define MAX_DISPLACEMENT 64 //Del openmv en el modo normal

/***************************************Definiciones***************************************************/
typedef enum {OPENMV_FOLLOW_LINE, OPENMV_FORK_LEFT, OPENMV_FORK_RIGHT, OPENMV_MERGE, OPENMV_ERROR,OPENMV_IDLE}openMV_states; //Los distintos estados del OpenMV
typedef enum {MISSION_SLOW_DOWN, MISSION_SPEED_UP, MISSION_FORK_LEFT, MISSION_FORK_RIGHT, MISSION_STATION, MISSION_MERGE,WAIT_FOR_MISSION}Mission_states; //Los distintos objetivos de la mision

typedef struct  {
  int displacement;
  bool tag_found;
  bool form_passed;
  bool error;
  String tag;
}openMV_msg; //La información que trae cada mensaje del openMV.


//Misiones hardcodeadas: 024    450

/***************************************Declaración funciones***************************************************/
openMV_msg decode_openMV_msg(byte *openMV_msg_buff);
void answer(openMV_msg msg);
void send_openMV_next_state(int urr_mision_step);
void print_openmv_msg(openMV_msg msg);
void recieve_mission();

/***************************************Variables globales***************************************************/
ArduinoQueue<int> mission_steps(20); //Máximo 20 pasos de misiones 
int curr_mission_step;

/***************************************Inicialización***************************************************/
void setup() {
  // initialize both serial ports:
  Serial.begin(115200);
  Serial1.begin(38400);
  byte openMV_msg;
  Serial1.setTimeout(20000);
  Serial.setTimeout(20000);
  Serial.print("Waiting for OpenMV");
  while(!Serial1.available());
  openMV_msg=Serial1.read(); //Espero que se inicialice el openmv
  Serial1.write(OPENMV_IDLE); //Se lo configura al openMV para que quede en espera hasta llegar una misión
  Serial.println(openMV_msg);
  Serial.println("Connected");
  
  void recieve_mission();
  curr_mission_step=mission_steps.dequeue();
  
  pinMode(ON_BOARD_LED_PIN,OUTPUT); //Puedo usar el LED para indicar que tan desplazado está.
}

/***************************************Loop principal***************************************************/
void loop() {
  // read from port 1, send to port 0:
  if(curr_mission_step == WAIT_FOR_MISSION)
    recieve_mission();
  else if(Serial1.available())
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
/***************************************Funciones***************************************************/
void recieve_mission()
{
  Serial.print("Give me a mission!");
  String s = Serial.readStringUntil('\n');
  unsigned int i = 0;
  for(i=0;i<s.length();i++)
    mission_steps.enqueue(int(s[i]-'0'));
  curr_mission_step=mission_steps.dequeue();
  send_openMV_next_state(curr_mission_step);
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

openMV_msg decode_openMV_msg(byte *openMV_msg_buff) //Del mensaje de UART traduce a las variables utilizadas en el arduino
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
void answer(openMV_msg msg) //Update del camino al openMV frente a distintos eventos
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
      curr_mission_step=mission_steps.dequeue();
      send_openMV_next_state(curr_mission_step);
    }
    else if ((curr_mission_step == MISSION_FORK_LEFT) && msg.form_passed)
    {
      curr_mission_step=mission_steps.dequeue();
      send_openMV_next_state(curr_mission_step);
    }
    else if ((curr_mission_step == MISSION_STATION) && msg.tag_found && msg.tag=="Station tag")
    {
      if(mission_steps.isEmpty())
        curr_mission_step = WAIT_FOR_MISSION;
      else
        curr_mission_step=mission_steps.dequeue();
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
  else if(curr_mision_step == MISSION_MERGE)
    Serial1.write(OPENMV_MERGE);
  else if(curr_mision_step == WAIT_FOR_MISSION)
    Serial1.write(OPENMV_IDLE);
}
