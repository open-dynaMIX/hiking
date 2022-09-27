<div align="center">
<h1>hiking</h1>

<img src="https://badgen.net/badge/python/3.10/blue?icon=python" alt="Python version 3.10">
<a href="https://github.com/open-dynaMIX/hiking"><img src="https://img.shields.io/badge/coverage-YOLO-ff00ff" alt="coverage 0%"></a>
<a href="https://github.com/ambv/black"><img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="code style black"></a>
<a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/github/license/open-dynaMIX/hiking.svg" alt="license MIT"></a>

<div style="font-family:Papyrus,serif">
    <h2><i>nom nom hike data ➡ 💩 stats</i></h2>
    <h3>your typical *it started as a small script* thingy</h3>
</div>

<pre>
$ python -m hiking show                                                                   
                                           Hikes                                           
 ───────────────────────────────────────────────────────────────────────────────────────── 
  ID   Date         Name                    ➡ km       ⬈ m       ⬊ m          ⏱      km/h  
 ───────────────────────────────────────────────────────────────────────────────────────── 
   1   2022-02-24   endorsement hike         5.0       298       298      01:15      4.00  
   2   2022-02-26   abnegation hike          5.0       298       298      01:15      4.00  
   3   2022-02-27   depositor hike           7.4      1029        54      02:45      2.69  
   4   2022-02-28   adrenaline's hike        6.6       420       420      02:00      3.30  
   5   2022-03-05   shooter's hike           5.0       288       288      01:50      2.73  
   6   2022-03-06   ofttimes hike            6.6       420       420      01:27      4.55  
   7   2022-03-09   fiend's hike             8.4       614       623      02:22      3.55  
   8   2022-03-21   witty hike               8.0       593       602      02:00      4.00  
   9   2022-04-03   forefathers hike         3.8       194       194      00:45      5.07  
  10   2022-04-04   regrow hike              3.8       194       194      00:45      5.07  
  11   2022-04-05   Rev hike                 3.8       194       194      00:45      5.07  
  12   2022-04-19   skirmishing hike         3.6       232       232      01:30      2.40  
  13   2022-05-20   surmount hike            4.8       287       287      01:00      4.80  
  14   2022-06-10   befall hike              6.5       418       418      01:41      3.86  
  15   2022-06-12   willies hike             9.9       614       669      02:15      4.40  
  16   2022-06-21   Charlotte hike           4.9       290       290      01:05      4.52  
  17   2022-06-22   nominative hike          4.7       297       297      01:15      3.76  
  18   2022-06-23   staking hike             6.4       429       429      01:32      4.17  
  19   2022-07-02   fumigation's hike       20.7      2040      2028      07:14      3.38  
 ───────────────────────────────────────────────────────────────────────────────────────── 
       STATS        19                  Σ: 124.9   Σ: 9149   Σ: 8235   Σ: 34:41         -  
                                          ⌀: 6.6    ⌀: 482    ⌀: 433   ⌀: 01:49   ⌀: 3.96  
                                         ↑: 31.2   ↑: 2040   ↑: 2028   ↑: 07:14   ↑: 5.07  
                                          ↓: 3.6    ↓: 194     ↓: 54   ↓: 00:45   ↓: 2.40  
 ───────────────────────────────────────────────────────────────────────────────────────── 
</pre>

<pre>
$ python -m hiking show 19                                                                
fumigation's hike                                                                         
──────────────────────────────────────                                                    
ID            19                                                                          
Date          2022-07-02                                                                  
➡ km          20.7                                                                        
⬈ m           2040                                                                        
⬊ m           2028                                                                        
⏱            06:07                                                                      
km/h          3.38                                                                        
──────────────────────────────────────                                                    
                                                                                          
(elevation (m)) ^                                                                         
      2269 |                                                                              
      2169 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      2069 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      1969 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⠞⠀⠈⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      1869 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡏⠀⠀⠀⠈⢧⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      1769 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡞⠀⠀⠀⠀⠀⠀⠘⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      1669 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡞⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      1569 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠳⡄⠀⠀⢠⠦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      1469 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡄⢠⠏⠀⠹⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      1369 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡤⠶⣄⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠋⠀⠀⠀⠸⣄⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      1268 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠋⠀⠀⠈⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠘⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      1168 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡤⠚⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
      1068 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⡼⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
       968 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⡾⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢳⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
       868 | ⡇⠀⠀⠀⠀⠀⠀⠀⡞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
       768 | ⡇⠀⠀⠀⠀⠀⢀⡜⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
       668 | ⡇⠀⠀⠀⣀⣰⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⣆⠀⠀⠀⠀⠀⠀⠀⠀      
       568 | ⡇⠀⢠⠞⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⢆⠀⠀⠀⠀⠀⠀⠀      
       468 | ⡇⣠⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧⡀⠀⠀⠀⠀⠀      
       368 | ⡏⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⠀⠀      
       268 | ⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀      
-----------|-|---------|---------|---------|---------|---------|---------> (Distance (km))
           | 0.00      3.92      7.85      11.77     15.70     19.62                      
</pre>
</div>

 * linux only probably idc
 * python>=3.10 only - gonna try the new goodies
 * CLI only coz your js sucks
 * no tests coz life is short
 * no releases, learn to python
 * no docs kinda, try `--help` or read the code

[Dependencies](https://github.com/open-dynaMIX/hiking/blob/main/pyproject.toml#L10)
