import processing.pdf.*;

String[] lines;
int index = 0;
int x,y,ma=0;

void setup() {
  size(2*700,2*500);
  int cols = width;
  int rows = height;
  background(255);
  
  lines = loadStrings("matrix700x500.csv");
  //checkmax();
  //beginRecord(PDF, "heatmap.pdf"); 
  ellipseMode(CENTER);
}

//void checkmax() {
//  int val=0;
//  for (y=0; y<lines.length; y++) {
//    String[] row = split(lines[y], ',');
//    for (x=0; x<row.length; x++) {
//      val = int(row[x]);
//      if (val > ma) ma = val;
//    }
//  }
//  println("Max " + ma);
//  y=0;
//}

void draw() {
  if ( (y < 500)) {
    String[] row = split(lines[y], ',');
    for (x=0; x<row.length; x++) {
      stroke(50, 155, 50, int(row[x])*28);
      fill(50, 155, 50, int(row[x])*28);
      ellipse(2*x+1,2*y+1,1,1);
    }
    y++;
  } else {
   // endRecord();
  }
}

