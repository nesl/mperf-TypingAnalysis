clc;
clear all;
close all;
%%
t1 = 0;
t2 = 40;
start_time = Time(1);
offset = 1; %in seconds
Time2 = (Time - Time(1))*1000;
end_time = Time2(end);
label_time = Time(1)*1000:40:Time(end)*1000;
labels = zeros(length(label_time),2);
labels(:,1) = label_time;
l = length(Time2);
%%
for i=1:l
    index = ceil((Time2(i)+1)/40);
    %labels(2,index) = Keys(i);
    labels(index,2) = KeyID(i);
end
%%
save('labels.mat','labels');
