function [ energyOutput ] = singleSolarArray(exceldatarray, singularPanelArea, singularPanelPower, hashed)
figure(1)
[~, ~, datarray]=xlsread(exceldatarray);

%calculating energy output vector
r=singularPanelPower./singularPanelArea;
%CHANGE THIS TO EXCEL FILE READ-IN!
H=360.*str2num(datarray{7,2});

header = datarray(:,1);
datarray(:,1) = [];


lats = datarray(5,[1:5]);
lats = cell2mat(lats);
longs = datarray(6,[1:5]);
longs = cell2mat(longs);

A = areafunction(longs,lats);

times=datarray(1,:);
%try this
% times = cell2mat(times)
times = datenum(times, 'yyyy-mm-dd HH:MM:SS');
[~,sort2] = sort(times);
datarray = datarray([1 2 3 4],sort2);

coverpercents=cell2mat(datarray(2,:));
azimuths=cell2mat(datarray(3,:));
heights=cell2mat(datarray(4,:));
times=datarray(1,:);
times = datenum(times, 'yyyy-mm-dd HH:MM:SS');

%Plotting the four graphs
subplot(2,2,1)
plot(times,coverpercents,'b.','MarkerSize',15)
title({'Percentage Cloud Cover Over Time', ''},'FontSize',11)
xlabel('Time','FontName','AvantGarde')
ylabel('Percent Cloud Coverage','FontName','AvantGarde')
axis square
set(gca,'XTickLabel','')
grid on
grid minor

subplot(2,2,4)
plot(times,azimuths,'r')
title({'Solar Azimuthal Angles Over Time', ''},'FontSize',11)
xlabel('Time','FontName','AvantGarde')
ylabel('Solar Azimuthal Angle (Degrees)','FontName','AvantGarde')
axis square
set(gca,'XTickLabel','')
grid on
grid minor

subplot(2,2,3)
plot(times,heights,'r')
axis equal
title({'Solar Elevation Over Time', ''},'FontSize',11)
xlabel('Time','FontName','AvantGarde')
ylabel('Solar Elevation (Degrees)','FontName','AvantGarde')
axis square
set(gca,'XTickLabel','')
grid on
grid minor

%finish finding Energy parameters
PR=1-coverpercents;
 
energyOutputs=(A.*r.*H).*PR;

%Finish plotting
subplot(2,2,2)
p = plot(times,energyOutputs,'b.','MarkerSize',15);
set(figure(1), 'Position',[0 0 1000 750])
axis equal
title({'Energy Output of Solar Array Over Time', ''},'FontSize',11)
xlabel('Time','FontName','AvantGarde')
ylabel('Energy Output (Kilowatt Hours-kWh)','FontName','AvantGarde')
axis square
set(gca,'XTickLabel','')
grid on
grid minor
path = ['./images/'  hashed  '.jpg'];
saveas(p,path);
temp = imread(path);
temp = imresize(temp, 0.40);
imwrite(temp, path);
energyOutput=mean(energyOutputs);

end
