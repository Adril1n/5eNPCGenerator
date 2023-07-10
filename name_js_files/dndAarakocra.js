var nm1=["","","","","","c","cl","cr","d","g","gr","h","k","kh","kl","kr","q","qh","ql","qr","r","rh","s","y","z"];
var nm2=["a","e","i","u","a","e","i","u","a","e","i","u","a","e","i","u","a","e","i","u","a","e","i","u","a","e","i","u","ae","aia","ee","oo","ou","ua","uie"];
var nm3=["c","cc","k","kk","l","ll","q","r","rr"];
var nm4=["a","e","i","a","e","i","a","e","i","a","e","i","a","e","i","aa","ea","ee","ia","ie"];
var nm5=["","","","","c","ck","d","f","g","hk","k","l","r","rr","rc","rk","rrk","s","ss"];

function nameMas() {
	rnd=Math.random()*nm1.length|0;
	rnd2=Math.random()*nm2.length|0;
	rnd3=Math.random()*nm5.length|0;

	if (Math.random() >= 0.5) {
		while (nm1[rnd]===nm5[rnd3]) {
			rnd3=Math.random()*nm5.length|0;
		}
		nMs=nm1[rnd]+nm2[rnd2]+nm5[rnd3];
	}
	else {
		rnd4=Math.random()*nm3.length|0;
		rnd5=Math.random()*nm4.length|0;
		nMs=nm1[rnd]+nm2[rnd2]+nm3[rnd4]+nm4[rnd5]+nm5[rnd3];
	}
	return nMs
}