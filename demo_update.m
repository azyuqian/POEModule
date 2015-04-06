function [ PARA ] = demo_update( fName, newData )
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

    SECPERSEC  = 1;
    SECPERMIN  = 60*SECPERSEC;
    SECPERHOUR = 60*SECPERMIN;
    SECPERDAY  = 24*SECPERHOUR;
    SECPERMON  = 30*SECPERDAY;
    SECPERYEAR = 12*SECPERMON; %#ok<NASGU>
    
%have to modify time_inst and #row&cols for ploting

    time_inst = newData(end-2)*SECPERHOUR+newData(end-1)*SECPERMIN+newData(end);
    
    %n_time_para = 6;
    plot_n_row = 1;
    plot_n_col = 1;

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

        subplot(plot_n_row,plot_n_col,1);
        if(~isempty(PARA{7}))
            x = PARA{7}(end,1); y = PARA{8}(end,1); plot(x,y,'r.','markersize', 40); grid;
            xlabel('Position in x'); ylabel('Position in y');
            title('Joystick Position'); set(gca,'FontSize',12);
            axis([Xmin,Xmax,Ymin,Ymax]); 
            %ax = gca;
            %ax.XTickLabel = {'Leftmost','Centre','Rightmost'};
            %ax.YTickLabel = {'Uppermost','Centre','Lowermost'};
        end
%         subplot(plot_n_row,plot_n_col,5); title('Humidity Profile');
%         ylabel('Relative Humidity (%)');       ylim([hum_min,hum_max]);
        
        save(fNameToSave,'PARA','-v6');
    end
        
end

