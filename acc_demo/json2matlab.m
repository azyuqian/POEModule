function [] = json2matlab( jsonFile_acce, jsonFile_temh, matlFile_acce, matlFile_temh )
%converts json type file to matlab type file

    acce = importdata(jsonFile_acce);
    temh = importdata(jsonFile_temh);
    
    l1 = length(acce); l2 = length(temh);
    
    ACCE = zeros(l1,3);
    for i = 1:l1
        temp = acce(i);
        temp = JSON.parse(temp{1,1});
        ACCE(i,:) = [temp.x, temp.y, temp.z];
    end
    
    TEMH = zeros(l2,2);
    for i = 1:l2
        temp = temh(i);
        temp = JSON.parse(temp{1,1});
        TEMH(i,:) = [temp.temperature, temp.humidity];
    end
    
    save(matlFile_acce,'ACCE','-ascii');
    save(matlFile_temh,'TEMH','-ascii');

end

