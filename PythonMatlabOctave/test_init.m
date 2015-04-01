function [ PARA ] = test_init( fName )
% data are in the format of :
% PARA1 PARA2 ... PARAn yyyy mm dd hh minmin ss 
% i.e. last six numbers for time
% e.g. [1,2,3,55,0,NaN,4,9999,6,2015,04,01,01,02,03]

% example use: 
% filename = 'data.txt'; 
% test_init(filename);
% 
% or: test_init('test.txt')

%have to modify time_inst and #row&cols for ploting

    n_time_para = 6;
    plot_n_row = 3;
    plot_n_col = 3;
    
    tem_min = -40;
    tem_max = 120;
    hum_min  = 0;
    hum_max  = 100;

    [~,name,ext] = fileparts(fName);
    fNameToSave = strcat(name,'.mat');
    if (~strcmp(ext,'.txt'))
        disp('Database file should instead have extension ".txt",');
        disp('looking for corresponding".txt"...');
        fName = strcat(name,'.txt');
    end
    
    if (~exist(fName,'file'))
        disp('File does not exist, a new one will be created.');
        temp = []; %#ok<NASGU>
        save(fName,'temp','-ASCII');
    end

    data = load(fName);

    if (~isempty(data))
        %numrow = size(data,1);  % #time instances
        numpara = size(data,2)-n_time_para;  % #parameters
       
        PARA=cell(numpara,1);
        for i = 1:numpara
            TEMP = data(:,i);
            T_TEMP = data(:,end-2)*3600+data(:,end-1)*60+data(:,end);
            LOGIC_TEMP = TEMP < 9999;
            PARA{i} = [TEMP(LOGIC_TEMP), T_TEMP(LOGIC_TEMP)];
        end

        for i = 1:numpara
            subplot(plot_n_row,plot_n_col,i);
            
            if(~isempty(PARA{i}))
                x = PARA{i}(:,2); y = PARA{i}(:,1); plot(x,y); grid; 
                xlabel('Time Elapsed (s)'); set(gca,'FontSize',12);
                if(x(end)>x(1))
                    xlim([x(1),x(end)]);
                elseif(x(end)<x(1))
                    error('Error in time calculation. (x(end) <= x(1))');
                end
            end
        end
        
        subplot(plot_n_row,plot_n_col,1); title('Acceleration Profile in x');
        ylabel('Acceleration in x (ms^{-2})'); 
        
        subplot(plot_n_row,plot_n_col,2); title('Acceleration Profile in y');
        ylabel('Acceleration in y (ms^{-2})');
        
        subplot(plot_n_row,plot_n_col,3); title('Acceleration Profile in z');
        ylabel('Acceleration in z (ms^{-2})');

        subplot(plot_n_row,plot_n_col,4); title('Temperature Profile');
        ylabel('Temperature (^oC)');           ylim([tem_min,tem_max]);
        
        subplot(plot_n_row,plot_n_col,5); title('Humidity Profile');
        ylabel('Relative Humidity (%)');       ylim([hum_min,hum_max]);
    else
        if (~exist(fNameToSave,'file'))
            disp('An empty ".mat" file is also created.');
        end
        disp('Database is empty, please update new data.');
        PARA = [];
    end
    
    save(fNameToSave,'PARA','-v6');

end

