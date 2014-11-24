clear;close;clc;
% Use Ctrl+c to terminate the program

g = 9.8;

figure;
plot3(0,0,0,'k');

while(1)
    prob = 0.5;
    plummet = rand > prob;
    A = [0,0,-g];
    B = (rand(1,3)-0.5)*20;
    A = plummet*A + (1-plummet)*B;

    fid = fopen('data.txt','a'); % fileID
    format = '%.2f %.2f %.2f\n'; % format to be written
    fprintf(fid, format, A); % write values at end of file
    fclose(fid); % close the file 
%     type data.txt

    data = importdata('data.txt');
    tip = data(end,:);
    x_max = abs(tip(1))*1.1;
    y_max = abs(tip(2))*1.1;
    z_max = abs(tip(3))*1.1;  
    xyz_max = [x_max, y_max, z_max];
    XYZ = xyz_max == 0;
    xyz_max(XYZ) = 1;
    x_max = xyz_max(1);
    y_max = xyz_max(2);
    z_max = xyz_max(3);
    
    plot3(0,0,0,'k');
%     axis([-x_max,x_max,-y_max,y_max,-z_max,z_max]);
    axis([-1.05*g,1.05*g,-1.05*g,1.05*g,-1.05*g,1.05*g])
    arrow([0,0,0],tip,10,'BaseAngle',20);
    grid on;
    pause(0.1)
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
