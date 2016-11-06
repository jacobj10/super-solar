function [area] = areafunction (longs,lats)
earthellipsoid = referenceSphere('earth','m');
area = areaint(lats, longs, earthellipsoid);
%outputs function in m^2
end
