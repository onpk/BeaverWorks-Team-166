var nsch = 11;
var nsum = 3;
var nvg = 3;
var nspt = 5;
var nscsm = 3;
var nt = 2;

var tsch = 20;
var tsum = 5;
var tvg = 3;
var tspt = 6;
var tscsm = 3;
var tt = 3;

console.log("Amount Remaining")
document.getElementById("sch").textContent="School".concat(" (", nsch.toString(), ")");
document.getElementById("sum").textContent="Summer".concat(" (", nsum.toString(), ")");
document.getElementById("vg").textContent="Video Games".concat(" (", nvg.toString(), ")");
document.getElementById("spt").textContent="Sports".concat(" (", nspt.toString(), ")");
document.getElementById("scsm").textContent="Sarcasm".concat(" (", nscsm.toString(), ")");
document.getElementById("t").textContent="Texting".concat(" (", nt.toString(), ")");

var psch = document.getElementById("psch");
var psum = document.getElementById("psum");
var pvg = document.getElementById("pvg");
var pspt = document.getElementById("pspts");
var pscsm = document.getElementById("pscsm");
var pt = document.getElementById("pt");

console.log("Setting progress bar width");
psch.style.width = ((tsch - nsch)/tsch)*100 + "px";
psum.style.width = ((tsum - nsum)/tsum)*100 + "px";
pvg.style.width = ((tvg - nvg)/tvg)*100 + "px";
pspt.style.width = ((tspt - nspt)/tspt)*100 + "px";
pscsm.style.width = ((tspt - nspt)/tspt)*100 + "px";
pt.style.width = ((tt - nt)/tt)*100 + "px";