function makeRunMats(subjID)
%   import events csv and convert to runN.mat files in /events/glm/ directory
%
%   Parameters
%   ----------
%   subjID : int
%        simply subject ID in integers (ie. 5, 10, 25)
%
%   Returns
%   -------
%   runN.mat : mat
%        struct with duration, condition, stimOnset information


% function variables (Do not change unless you know what you are doing)
%---------------------------------------------------------------------%
baseDir = '/scratch/polynlab/fmri/cdcatmr/';  % scratch data dir
ntrials = 8;
%---------------------------------------------------------------------%

number_tag = num2str(subjID, '%03.f');
% set path
subject = ['cdcatmr', number_tag];
subjDir = [baseDir, subject];


% look for the final events file from annotation code
if isfile([subjDir, '/events/', subject, 'events.csv'])
    % import csv as table then convert to struct
    tblEvents = readtable([subjDir, '/events/', subject, 'events.csv']);
        
    events = table2struct(tblEvents);
        
    durations = zeros(1,27); 
    durations = num2cell(durations);
        
    for t = 1:ntrials
            
        % trial subset
        trial = events([events.trialN] == t);
        
        % stim pres subset
        stimPres = trial(strcmp({trial.types}, 'stim_pres'));
            
        names = {stimPres.item};
        
        % scan N
        onsets = {stimPres(:).start_scan};
        
        cd([subjDir, '/events']);
        
        if ~isfolder('glm')
            mkdir glm;
        end
        
        save([subjDir, '/events/glm/run' num2str(t) '.mat'], 'onsets','durations','names')
        disp(['Successfully saved for ', [subjDir, '/events/glm/run' num2str(t) '.mat']])
    end
end
    
end