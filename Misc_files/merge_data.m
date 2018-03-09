clc;
clear all;
close all;
%%
acc_l = importdata('raw\raw7\2017112317_7.csv');
acc_r = importdata('raw\raw15\2017112317_15.csv');
gyro_l = importdata('raw\raw5\2017112317_5.csv');
gyro_r = importdata('raw\raw13\2017112317_13.csv');
led_l = importdata('raw\raw9\2017112317_9.csv');
led_r = importdata('raw\raw17\2017112317_17.csv');

left_wrist = [acc_l(:,1), acc_l(:,3:5), gyro_l(:,3:5), led_l(:,3:5)];
right_wrist = [acc_r(:,1), acc_r(:,3:5), gyro_r(:,3:5), led_r(:,3:5)];

left_ts = timeseries(left_wrist(:,2:end),left_wrist(:,1));
right_ts = timeseries(right_wrist(:,2:end),right_wrist(:,1));
[ts1 ts2] = synchronize(left_ts, right_ts,'Uniform','Interval',40)

%%
left_data = [ts1.Time, ts1.Data];
right_data = [ts2.Time, ts2.Data];
save('left_data.mat','left_data');
save('right_data.mat','right_data');

%%
acc = [ts2.Time, ts2.Data];
t1 = 0;
t2 = 40;
start_time = Time(1);
offset = 1; %in seconds
Time2 = Time - Time(1);
acc(:,1) = acc(:,1)/1000 - start_time - offset;
acc = acc(acc(:,1)>0,:);
%%
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
plot(acc_t(:,1),acc_t(:,2));
subplot(4,1,2);
plot(acc_t(:,1),acc_t(:,3));
subplot(4,1,3);
plot(acc_t(:,1),acc_t(:,4));
l = length(Time_t);
key_press = ones(l,1);
subplot(4,1,4);
stem(Time_t,special_keys);
xlim([t1,t2]);