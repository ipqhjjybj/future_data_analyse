inputs:
	//eyuxian
	CF(5),
	CM(8),
	CS(13),
	d_CF(3),
	d_CM(5),
	d_CS(8),
	
	//lots
	lots(1),
	
	//zhangdie
	N_up(10),
	N_down(10),
	
	//zhisun
	zhisunlv_l(10),
	zhisunlv_s(10);

variables: 
	//eyuxian
	lips(0),
	teeth(0),
	croco(0),
	lips_N(0),
	teeth_N(0),
	croco_N(0),
	zui(0),
	col_lips(0),
	col_teeth(0),
	col_croco(0),
	
	//eyuxian_xinhao
	eyu(0),
	
	//kai_zhangdiexian
	kai_up(0),
	kai_down(0),
	col_kai_up(0),
	col_kai_down(0),
	
	//zhisun
	zhisun_l(0),
	zhisun_s(0),
	high_since_entry(0),
	low_since_entry(0),
	col_high(0),
	col_low(0),
	col_zhisun_l(0),
	col_zhisun_s(0);
	
	
//=====================================================================================================================
//eyuxian_zhibiao
lips_N=XAverage(Close,CF);
teeth_N=XAverage(Close,CM);
croco_N=XAverage(Close,CS);
lips=lips_N[d_CF];
teeth=teeth_N[d_CM];
croco=croco_N[d_CS];

//col_lips=tl_new(date[1],time[1],lips[1],date,time,lips);
//tl_setcolor(col_lips,green);
//col_teeth=tl_new(date[1],time[1],teeth[1],date,time,teeth);
//tl_setcolor(col_teeth,red);
//col_croco=tl_new(date[1],time[1],croco[1],date,time,croco);
//tl_setcolor(col_croco,blue);

//eyuxian_zui
if (lips>teeth and teeth>croco) then
begin
	zui=1;
end
else
begin
	if (lips<teeth and teeth<croco) then
	begin
		zui=-1;
	end
	else
	begin
		zui=0;
	end;
end;
//text_new(date,time,high+5,text(zui));


//=====================================================================================================================
//eyuxian_xinhao
//long
if(zui=1 and  Close>Open and Low>lips ) then
begin
	eyu=1;
end;
if (eyu[1]=1 and low<lips ) then
begin
	eyu=0;
end;

//short
if(zui=-1 and  Close<Open and High<lips ) then
begin
	eyu=-1;
end;
if (eyu[1]=-1 and high>lips) then
begin
	eyu=0;
end;
//text_new(date,time,high+5,text(eyu));


//=====================================================================================================================
//kai_zhangdiexian
if (eyu[1]=0 and eyu=1 ) then
begin
	kai_up=close+N_up*MinMove*PriceScale;
end;
if (eyu[1]=0 and eyu=-1 ) then
begin
	kai_down=close-N_down*MinMove*PriceScale;
end;

//col_kai_up=tl_new(date[1],time[1],kai_up[1],date,time,kai_up);
//tl_setcolor(col_kai_up,yellow);
//col_kai_down=tl_new(date[1],time[1],kai_down[1],date,time,kai_down);
//tl_setcolor(col_kai_down,cyan);

//=====================================================================================================================
//entry
//long
if (zui>0 and marketposition<1 and eyu > 0) then
begin
	buy lots contract next bar kai_up stop;
end;

//short
if (zui<0 and marketposition>-1) then
begin
	sellshort lots*absvalue(eyu) contract next bar  kai_down stop;
end;


//=====================================================================================================================
//zhisunxian
//zhisunxian_l
if (barssinceentry=0)then
begin
	high_since_entry=high;
end;
if (marketposition>0 and high>high_since_entry) then
begin
	high_since_entry=high;
end;
if (marketposition>0) then
begin
	zhisun_l=high_since_entry*(1-zhisunlv_l/1000);
end;

//zhisunxian_s
if (barssinceentry=0)then
begin
	low_since_entry=low;
end;
if (marketposition<0 and low<low_since_entry) then
begin
	low_since_entry=low;
end;
if (marketposition<0) then
begin
	zhisun_s=low_since_entry*(1+zhisunlv_s/1000);
end;

//col_high=tl_new(date[1],time[1],high_since_entry[1],date,time,high_since_entry);
//tl_setcolor(col_high,yellow);
//col_low=tl_new(date[1],time[1],low_since_entry[1],date,time,low_since_entry);
//tl_setcolor(col_low,cyan);

//col_zhisun_l=tl_new(date[1],time[1],zhisun_l[1],date,time,zhisun_l);
//tl_setcolor(col_zhisun_l,yellow);
//col_zhisun_s=tl_new(date[1],time[1],zhisun_s[1],date,time,zhisun_s);
//tl_setcolor(col_zhisun_s,cyan);



//=====================================================================================================================
//zhisun
//long
if (marketposition>0) then
begin
	sell lots contract next bar zhisun_l stop;
end;

//short
if (marketposition<0) then
begin
	buytocover lots contract next bar zhisun_s stop;
end;















	
	
	
