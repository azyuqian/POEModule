clear;close;clc;
% Use Ctrl+c to terminate the program

jsonFile_acce = 'Data_accelerometer.txt';
jsonFile_temh = 'Data_Temp_Hum.txt';
matlFile_acce = 'data_acce.txt';
matlFile_temh = 'data_temh.txt';

json2matlab( jsonFile_acce, jsonFile_temh, matlFile_acce, matlFile_temh );
fileName_acce = matlFile_acce; fileName_temh = matlFile_temh;

freq_acce = 2; % in Hz
freq_temh = 2; % in Hz
freq = lcm(freq_acce,freq_temh);

g = 9.8; am = ceil(g);

tem_min = -40;
tem_max = 120;
hu_min = 0;
hu_max = 100;

figure;

while(1)
% %     plummet = rand < prob_static;
% %     A = [0,0,-g]; B = (rand(1,3)-0.5)*20;
% %     A = plummet*A + (1-plummet)*B;
% %     
% %     % acce_data
% %     fid = fopen(fileName_acce,'a'); % fileID of accelerometer
% %     format = '%.2f %.2f %.2f\n'; % format to be written
% %     fprintf(fid, format, A); % write values at end of file
% %     fclose(fid); % close the file 

    acce_data = importdata(fileName_acce);
    X = acce_data(:,1); Y = acce_data(:,2); Z = acce_data(:,3);
    t1 = length(X); t1 = (1:t1)/freq_acce;
    tip = acce_data(end,:);
    
    
    
% %     TH = [25,80];
% %     
% %     % temh_data
% %     fid = fopen(fileName_temh,'a'); % fileID of temperature and humidity sensor
% %     format = '%.2f %.2f\n'; %format to be written
% %     fprintf(fid, format, TH); % write values at end of file
% %     fclose(fid); % close the file 
    
    temh_data = importdata(fileName_temh);
    TEM = temh_data(:,1); HU = temh_data(:,2);
    t2 = length(TEM); t2 = (1:t2)/freq_temh;


    subplot(2,3,1);plot3(0,0,0,'k',0,0,0,'k',0,0,0,'k');
    axis([-am,am,-am,am,-am,am]);
    arrow([0,0,0],tip,10,'BaseAngle',20);
    xlabel('Acceleration in x (ms^{-2})');
    ylabel('Acceleration in y (ms^{-2})');
    zlabel('Acceleration in z (ms^{-2})');
    xleg = sprintf('a_x = %.2f ms^{-2}', tip(1));
    yleg = sprintf('a_y = %.2f ms^{-2}', tip(2));
    zleg = sprintf('a_z = %.2f ms^{-2}', tip(3));
    legend(xleg,yleg,zleg);
    title('Real Time Acceloration');
    set(gca,'FontSize',12);
    grid on;
    
    subplot(2,3,2); plot(t1,X); title('Acceleration Profile in x');
    xlabel('Time Elapsed (s)'); ylabel('Acceleration in x (ms^{-2})'); grid;
    set(gca,'FontSize',12);
    subplot(2,3,4); plot(t1,Y); title('Acceleration Profile in y');
    xlabel('Time Elapsed (s)'); ylabel('Acceleration in y (ms^{-2})'); grid;
    set(gca,'FontSize',12);
    subplot(2,3,5); plot(t1,Z); title('Acceleration Profile in z');
    xlabel('Time Elapsed (s)'); ylabel('Acceleration in z (ms^{-2})'); grid;
    set(gca,'FontSize',12);
    
    subplot(2,3,3); plot(t2,TEM); title('Temperature Profile');
    xlabel('Time Elapsed (s)'); ylabel('Temperature (^oC)'); grid;
    set(gca,'FontSize',12); ylim([tem_min,tem_max]);
    subplot(2,3,6); plot(t2,HU); title('Humidity Profile');
    xlabel('Time Elapsed (s)'); ylabel('Relative Humidity (%)'); grid;
    set(gca,'FontSize',12); ylim([hu_min,hu_max]);
    
    pause(1/freq)
end



% rs = 10; %retracting times
% TIP = [];
% for i = 1:length(tip)
%     temp = tip(i);
%     TEMP = temp:-temp/rs:0;
%     TIP = [TIP TEMP']; %#ok<AGROW>
% end
% 
% for i = 1:length(TEMP)
%     plot3(0,0,0);
%     axis([-x_max,x_max,-y_max,y_max,-z_max,z_max]);
%     arrow([0,0,0],TIP(i,:),10,'BaseAngle',20);
%     grid on;
%     pause(1e-100);
% end
% 
% plot3(0,0,0,'k');
% grid on;
% axis([-x_max,x_max,-y_max,y_max,-z_max,z_max]);
