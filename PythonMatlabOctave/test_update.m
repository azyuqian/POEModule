function [ PARA ] = test_update( fName, newData )
% data are in the format of :
% PARA1 PARA2 ... PARAn yyyy mm dd hh minmin ss 
% i.e. last six numbers for time
% e.g. [1,2,3,55,0,9999,4,9999,6,2015,04,01,01,02,03]

%have to modify time_inst and #row&cols for ploting

    time_inst = newData(end-2)*3600+newData(end-1)*60+newData(end);
    
    %n_time_para = 6;
    plot_n_row = 3;
    plot_n_col = 3;
    
    tem_min = -40;
    tem_max = 120;
    hum_min  = 0;
    hum_max  = 100;
    
    newData(newData>=9999) = NaN;
    
    [~,name,ext] = fileparts(fName);
    fNameToSave = strcat(name,'.mat');
    
    %check for validity
    if(~strcmp(ext,'.txt'))
        error('Expecting file name with ".txt" extension');
    elseif(~exist(fNameToSave,'file'))
        error('No corresponding ".mat" file generated yet. Should initialize first.');
    end
    
    data = load(fNameToSave);
    check_empty = fieldnames(data);
    
    if(isempty(data.(check_empty{1})))
        save(fName,'newData','-ASCII');
        test_init(fName);
    else
        name_para = fieldnames(data);
        PARA = data.(name_para{1});

        numpara = length(PARA);  % #parameters
        TEMP = newData(1:numpara);
        LOGICAL_TEMP = TEMP < 9999;

        DATA_UPDATE = TEMP(LOGICAL_TEMP);
        PARA_UPDATE = PARA(LOGICAL_TEMP);
        numupdate = sum(LOGICAL_TEMP);
        for i = 1:numupdate
            PARA_UPDATE{i} = [PARA_UPDATE{i};[DATA_UPDATE(i),time_inst]];
        end
        
        PARA(LOGICAL_TEMP) = PARA_UPDATE;

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
        
        save(fNameToSave,'PARA','-v6');    
    end
        
end

