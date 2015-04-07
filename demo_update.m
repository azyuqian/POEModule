function [ PARA ] = demo_update( fName, newData, whatToPlot )
% data are in the format of :
% PARA1 PARA2 ... PARAn yyyy mm dd hh minmin ss 
% i.e. last six numbers for time
% e.g. [1,2,3,55,0,9999,4,9999,6,2015,04,01,01,02,03]

% example use: 
% filename = 'data.txt'; 
% data_update=[1,2,3,55,0,9999,4,9999,6,2015,04,01,01,02,03];
% test_update(filename,data_update);
% 
% or: test_init('test.txt',[1,NaN,3,55,0,9999,4,9999,6,2015,04,01,01,02,03]);

    switch whatToPlot
        case 1 % Joystick
            toPlot = 7;
        case 2 % Temperature
            toPlot = 4;
        case 3 % Humidity
            toPlot = 5;
        case 4 % X
            toPlot = 1;
        case 5 % Y
            toPlot = 2;
        case 6 % Z
            toPlot = 3;
        case 7 % Motion
            toPlot = 6;
    end

    SECPERSEC  = 1;
    SECPERMIN  = 60*SECPERSEC;
    SECPERHOUR = 60*SECPERMIN;
    SECPERDAY  = 24*SECPERHOUR;
    SECPERMON  = 30*SECPERDAY;
    SECPERYEAR = 12*SECPERMON; %#ok<NASGU>
    
%have to modify time_inst and #row&cols for ploting

    time_inst = newData(end-2)*SECPERHOUR+newData(end-1)*SECPERMIN+newData(end);

    Xmin = 260; Xmax = 763; %xcentre = 516;
    Ymin = 253; Ymax = 769; %ycentre = 510;
    
    newData(~(newData<9999)) = NaN;
    
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
        save(fName,'newData','-ascii');
        demo_init(fName);
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
        
        switch toPlot
            case 7  % Joystick
                x = PARA{7}(end,1); y = PARA{8}(end,1); plot(x,y,'r.','markersize',40); grid;
                xlabel('Position in x'); ylabel('Position in y');
                title('Joystick Position'); set(gca,'FontSize',12);
                axis([Xmin,Xmax,Ymin,Ymax]);
            otherwise
                if(~isempty(PARA{toPlot}))
                    x = PARA{toPlot}(:,end); y = PARA{toPlot}(:,1);plot(x,y);
                    xlabel('Time Elapsed (s)'); grid; set(gca,'FontSize',12);
                    if(x(end)>x(1))
                        xlim([x(1),x(end)]);
                    elseif(x(end)<x(1))
                        error('Error in time calculation. (x(end) <= x(1))');
                    end
                end
        end
        
        switch toPlot
            case 1
                title('Acceleration Profile in x'); ylabel('Acceleration in x (ms^{-2})'); 
            case 2
                title('Acceleration Profile in y'); ylabel('Acceleration in y (ms^{-2})');
            case 3 
                title('Acceleration Profile in z'); ylabel('Acceleration in z (ms^{-2})');
            case 4
                title('Temperature Profile'); ylabel('Temperature (Celcius)');
            case 5
                title('Humidity Profile'); ylabel('Relative Humidity (%)');
            case 6
                title('Motion Detection'); ylabel('Motion Detected? (1 for yes, 0 otherwise)');
        end
        
        save(fNameToSave,'PARA','-v6');    
    end
        
end

