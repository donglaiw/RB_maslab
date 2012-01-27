cd img

a=dir('*.jpg');

for i=1:length(a)
movefile([a(i).name],['t' num2str(i) '.jpg']);
end
