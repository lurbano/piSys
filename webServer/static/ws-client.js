$(document).ready(function(){

  var WEBSOCKET_ROUTE = "/ws";

  if(window.location.protocol == "http:"){
      //localhost
      var ws = new WebSocket("ws://" + window.location.host + WEBSOCKET_ROUTE);
  }
  else if(window.location.protocol == "https:"){
      //Dataplicity
      var ws = new WebSocket("wss://" + window.location.host + WEBSOCKET_ROUTE);
  }

  ws.onopen = function(evt) {
      // $("#ws-status").html("Connected");
      // $("#ws-status").css("background-color", "#afa");
      // $("#server_light").val("ON");
      $("#signal").html("READY");
      $("#ws-status").html("Connected");
      $("#ws-status").css("background-color", "#afa");

      $("#logCheck").prop("checked", false);
      $("#timerCheck").prop("checked", false);
  };

  ws.onmessage = function(evt) {
      //console.log(evt);
      var sData = JSON.parse(evt.data);
      //console.log(sData);
      if (sData.sensor !== 'undefined'){
        //console.log(sData.info + "|" + )

        if (sData.info == 'hello'){
          r = sData.reply.toString();
          $("#HelloResponse").html(r);
        }

        //WHAT TO DO WHEN WE GET A MESSAGE FROM THE SERVER
        if (sData.info == 'timer'){
          m = sData.m.toString();
          s = sData.s.toString().padStart(2,"0");
          $("#timeLeft").html(m + ":" + s);
        }

        // TEMPERATURE SENSOR (1/2)

        // measure temperature once (button press)
        if (sData.info == 'S-one'){
          $("#sensor_measure").html(sData.S + ' ' + sData.units) //" °C");
          let now = new Date();
          $("#sensor_time").html(now.toString().split(" GMT")[0]);
        }

        // write all data to log at end of sensing
        if (sData.info == 'logT'){
          dataT.writeAllData(sData);
        }

        // continuous log: Add one data point to graph and table
        if (sData.info == 'logUp'){
          dataT.addRow(sData);
          graphT.addDataPoint(sData);

          $("#countdownData").html("-"+sData.timeLeft+" s");
          $("#timeLeftT").css("width", 100*sData.timeLeft/timeLog+"%");
        }
        //TEMPERATURE SENSOR (END)

        //LEDs
        // Activate LEDs
        if (sData.info == 'LEDsActive'){
          if (sData.active == "show") {
            $("#ledBlock").show();
            $("#hasLEDs").prop("checked", true);
            $("#nPix").val(sData.nPix);
          }
          else {
            $("#ledBlock").hide();
            console.log("LED's not activated by server. You may need to install the neoPixel library (see http://github.com/lurbano/rpi-led-strip)");
          }
        }
        //LEDs (END)

      };
  };

  ws.onclose = function(evt) {
      $("#ws-status").html("Disconnected");
      $("#ws-status").css("background-color", "#faa");
      $("#server_light").val("OFF");
  };

  //MESSAGES TO SEND TO THE SERVER

  // TEMPERATURE SENSOR (2/2)

  $("#logCheck").change(function(){
    if (this.checked){
      $(".logging").show();
    }
    else {
      $(".logging").hide();
    }

  })

  $("#checkSensor").click(function(){
      let msg = '{"what": "checkS"}';
      ws.send(msg);
      let return_signal = "Checking " + this.value.split(" ")[1];
      $("#sensor_measure").html(return_signal);
  });

  $("#monitorSensor").click(function(){
    let dt = $("#monitorSec").val();
    let msg = {
      "what": "monitor",
      "dt": dt
    };
    ws.send(JSON.stringify(msg));
  })

  $("#logT").click(function(){
      dataT = new dataTable("logData", "°C");
      dataT.setupTable();

      graphT = new dataGraph("logGraph", "°C");
      $("#logGraph").css("height", "400px");
      console.log(graphT.plot.data);

      let timeMin = parseInt($("#logT_timeMin").val());
      let timeSec = parseInt($("#logT_timeSec").val());
      timeLog = timeMin * 60 + timeSec;

      let dtMin = parseInt($("#logT_dtMin").val());
      let dtSec = parseInt($("#logT_dtSec").val());
      let dtMil = parseInt($("#logT_dtMil").val());
      let dt = (dtMin * 60 + dtSec) + (dtMil/1000);
      console.log(dt);

      let msg = {
        "what": "logT",
        "t": timeLog,
        "dt": dt,
        "update": "live"
      }
      ws.send(JSON.stringify(msg));
  });

  //TEMPERATURE SENSOR (END)

  //LEDs
  $("#hasLEDs").change(function(){
    let nPix = parseInt($("#nPix").val());
    console.log(this.checked, nPix);

    if (this.checked){
      var msg = {
        "what": "LEDs",
        "nPix": nPix,
        "activate": true
      }
      $(".ledControls").show();
    }
    else {
      var msg = {
        "what": "LEDs",
        "activate": false
      }
      $(".ledControls").hide();
    }

    ws.send(JSON.stringify(msg));

  })

  $("#nPixSet").click(function(){
    let nPix = parseInt($("#nPix").val());
    let msg = {
      "what": "nPixSet",
      "nPix": nPix
    }
    ws.send(JSON.stringify(msg));
  })
  //LEDs (END)

  $("#hello").click(function(){
      let msg = '{"what": "hello"}';
      ws.send(msg);
  });

  $("#timerCheck").change(function(){
    this.checked ? $(".timer").show() : $(".timer").hide();
  })
  $("#timer").click(function(){
      let m = $("#timerMin").val();
      let s = $("#timerSec").val();
      let msg = '{"what": "timer", "minutes":'+ m + ', "seconds": '+ s + '}';
      ws.send(msg);
  });

  $("#reboot").click(function(){
      let check = confirm("Reboot Pi?");
      if (check){
        var msg = '{"what": "reboot"}';
        ws.send(msg);
      }
  });


});



class dataTable{
  constructor(targetDiv, dataTitle){
    this.targetDiv = targetDiv;
    this.dataTitle = dataTitle;
  }
  setupTable(){
    this.table = document.createElement("table");
    let thead = this.table.createTHead();
    let row = thead.insertRow();

    let th = document.createElement('th');
    th.appendChild(document.createTextNode("time (s)"));
    row.appendChild(th);

    th = document.createElement('th');
    th.appendChild(document.createTextNode(this.dataTitle));
    row.appendChild(th);

    this.body = document.createElement('TBODY');
    this.table.appendChild(this.body);

    let tableDiv = document.getElementById(this.targetDiv);
    while (tableDiv.firstChild){
      tableDiv.removeChild(tableDiv.firstChild);
    }
    tableDiv.appendChild(this.table);
  }
  writeAllData(data){
    for (let i = 0; i< data.logData.length; i++){

      this.addRow(data.logData[i]);
    }
  }
  addRow(rowList){
    let tr = document.createElement("TR");

    let t = document.createElement("TD");
    t.appendChild(document.createTextNode(rowList["t"]));
    tr.appendChild(t);

    let val = document.createElement("TD");
    val.appendChild(document.createTextNode(rowList["x"]));
    tr.appendChild(val);

    this.body.appendChild(tr);
  }

}

class dataGraph{
  constructor(targetDiv, dataTitle){
    this.targetDiv = targetDiv;
    this.dataTitle = dataTitle;

    this.plot = document.getElementById(targetDiv);

    Plotly.newPlot( this.plot,
      [
        {
          type: 'scatter',
        	x: [],
        	y: []
        }
      ],
      {
        xaxis: {
          title: "time (s)"
        },
    	  yaxis: {
          title: this.dataTitle
        }
      }
    );

    this.plot.style.height = "300px";

  }
  addDataPoint( dataList ){
    let newx = parseFloat(dataList["t"]);
    let newy = parseFloat(dataList["x"]);
    //console.log(newx, newy);

    let update = { x: [[newx]], y: [[newy]]};
    //console.log(update);

    Plotly.extendTraces(this.plot, update, [0] );
  }
}
