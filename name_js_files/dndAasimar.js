var nm1=["","","","","b","br","c","cr","h","l","m","n","p","r","t","v","w","z"];var nm2=["a","e","i","o","u","y","a","e","i","o","u","y","a","e","i","o","u","y","au","ai","ea","ei"];var nm3=["d","dr","g","gg","gr","gw","k","kr","kl","l","ld","lg","lw","lr","lt","n","nr","nw","nl","r","rn","rr","rw","rl","v","vr","w"];var nm4=["a","i","a","i","a","i","a","i","a","i","a","i","e","a","i","e","a","i","e","o","o","u","u","ee","ia","ie","ai","ei"];var nm5=["d","l","m","n","t","v"];var nm6=["l","m","n","nt","r"];var nm7=["","","","","","br","d","dr","h","l","m","n","ph","r","rh","th","v","w","z"];var nm8=["a","i","o","a","i","o","a","i","o","a","i","o","a","i","o","a","i","o","e","e","ia","io","ea","eo"];var nm9=["d","j","l","ld","ldr","lv","ll","lt","m","mm","mn","n","nr","nv","nl","ndr","nm","r","rd","rk","rs","s","sr","sl","v"];var nm10=["a","e","i","o","a","e","i","o","a","e","i","o","a","e","i","o","a","e","i","o","ea","ia","ie"];var nm11=["l","m","n","r","s","z"];var nm12=["a","e","i","a","e","i","a","e","i","a","e","i","a","e","i","au","ou","oe"];var nm13=["","","","","","","","","","","","","","","","h","l","m","n","r"];

function nameFem(){rnd=Math.random()*nm7.length|0;rnd2=Math.random()*nm8.length|0;rnd3=Math.random()*nm9.length|0;rnd4=Math.random()*nm10.length|0;rnd5=Math.random()*nm13.length|0;if(Math.random<=0.5){while(nm9[rnd3]===nm7[rnd]||nm9[rnd3]===nm13[rnd5]){rnd3=Math.random()*nm9.length|0;}
nMs=nm7[rnd]+nm8[rnd2]+nm9[rnd3]+nm10[rnd4]+nm13[rnd5];}else{rnd6=Math.random()*nm11.length|0;rnd7=Math.random()*nm12.length|0;while(nm11[rnd6]===nm9[rnd3]||nm11[rnd6]===nm13[rnd5]){rnd6=Math.random()*nm11.length|0;}
nMs=nm7[rnd]+nm8[rnd2]+nm9[rnd3]+nm10[rnd4]+nm11[rnd6]+nm12[rnd7]+nm13[rnd5];}
return nMs}
function nameMas(){rnd=Math.random()*nm1.length|0;rnd2=Math.random()*nm2.length|0;rnd3=Math.random()*nm3.length|0;rnd4=Math.random()*nm4.length|0;rnd5=Math.random()*nm6.length|0;if(Math.random<=0.5){while(nm3[rnd3]===nm1[rnd]||nm3[rnd3]===nm6[rnd5]){rnd3=Math.random()*nm3.length|0;}
nMs=nm1[rnd]+nm2[rnd2]+nm3[rnd3]+nm4[rnd4]+nm6[rnd5];}else{rnd6=Math.random()*nm5.length|0;rnd7=Math.random()*nm4.length|0;while(nm5[rnd6]===nm3[rnd3]||nm5[rnd6]===nm6[rnd5]){rnd6=Math.random()*nm5.length|0;}
nMs=nm1[rnd]+nm2[rnd2]+nm3[rnd3]+nm4[rnd4]+nm5[rnd6]+nm4[rnd7]+nm6[rnd5];}
return nMs}