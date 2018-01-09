% clc;
% clear all;
% close all;

%acc = importdata('raw\raw7\2017112317_7.csv');
acc = importdata('raw\raw15\2017112317_15.csv');
t1 = 0;
t2 = 40;
start_time = Time(2);
offset = 1; %in seconds
Time2 = Time - Time(2);
acc(:,1) = acc(:,1)/1000 - start_time - offset;
acc = acc(acc(:,1)>0,:);

acc_t = acc(acc(:,1)<=t2,:);
Time_t = Time2(Time2<=t2);
acc_t = acc_t(acc_t(:,1)>t1,:);
Time_t = Time_t(Time_t>t1);
l = length(Time_t);
%Key IDs
% 160 - Shift
% 162 -  Ctrl
% 164 - Alt
% 13 - Enter
% 8 - Backspace
% 9 - Tab
special_keyids = [160, 162, 164, 13, 8, 9];
special_keys = zeros(l,1);

for i = 1:l
    if(ismember(KeyID(i), special_keyids))
        special_keys(i) = 1;
    end
end

subplot(4,1,1);
plot(acc_t(:,1),acc_t(:,3));
subplot(4,1,2);
plot(acc_t(:,1),acc_t(:,4));
subplot(4,1,3);
plot(acc_t(:,1),acc_t(:,5));
l = length(Time_t);
key_press = ones(l,1);
subplot(4,1,4);
stem(Time_t,special_keys);
xlim([t1,t2]);