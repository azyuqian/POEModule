clear;clc;close all;

fName = 'test_file.txt';
fName_s1 = 'test_saveddata1.txt';
fName_s2 = 'test_saveddata2.mat';
fName_s3 = 'test_saveddata3.mat';

% tic;
% toc;
% tic;
% data = importdata(fName);
% toc;
disp('Time took to load original ".txt" file:');
tic;
data = load(fName);
toc;
% tic;
% data = load(fName,'-mat');
% toc;
x   = data(:,1);
y   = data(:,2);
z   = data(:,3);
tem = data(:,4);
hum = data(:,5);
t   = data(:,6);

disp('Time took to save ASCII ".txt" file:');
tic;
save(fName_s1,'x','y','z','tem','hum','t','-ASCII');
toc;
disp('Time took to save ".mat" file:');
tic;
save(fName_s2,'x','y','z','tem','hum','t');
toc;
disp('Time took to save v6 ".mat" file:');
tic;
save(fName_s3,'x','y','z','tem','hum','t','-v6');
toc;

disp('Time took to load matlab-saved ASCII ".txt" file:');
tic;
data1 = load(fName_s1);
toc;
disp('Time took to load matlab-saved ".mat" file:');
tic;
data2 = load(fName_s2);
toc;
disp('Time took to load matlab-saved v6 ".mat" file:');
tic;
data3 = load(fName_s3);
toc;