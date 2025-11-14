import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os

CSV_FILE = 'personnelData/FULLpersonnel2020.csv'

GAME_ID_TO_VISUALIZE = '2020_01_ARI_SF'
PLAY_ID_TO_VISUALIZE = 653

def draw_field(ax, ydstogo, yardline_100):
    ax.set_facecolor('#3A9D23')
    
    # Set field boundaries
    max_y_visible = 45 # How many yards downfield to show
    ax.set_xlim(-25, 25)  # Sideline to sideline (approx 50 yards wide)
    ax.set_ylim(-10, max_y_visible)  # 10 yards into backfield

    # Draw endzone
    if pd.notna(yardline_100) and yardline_100 < max_y_visible:
        ax.axhspan(yardline_100, max_y_visible, color='#004080', alpha=0.5)
        ax.text(-24, yardline_100 + 1, 'ENDZONE', color='white', fontsize=12, fontweight='bold')
    
    # Draw line of scrimmage
    ax.axhline(0, color='white', linestyle='--', linewidth=2, label='Line of Scrimmage')
    
    # Draw first down line
    if pd.notna(ydstogo) and ydstogo < max_y_visible:
        ax.axhline(ydstogo, color='yellow', linestyle='-', linewidth=3, label=f'1st Down ({int(ydstogo)} yds)')
    
    # Draw yard lines
    if pd.isna(yardline_100):
        for y in range(5, max_y_visible, 5):
            if (pd.notna(ydstogo) and y == ydstogo):
                continue
            ax.axhline(y, color='white', linestyle='-', alpha=0.5)
            ax.text(-24, y + 0.5, str(y), color='white', fontsize=10)
    else:
        ball_on_yardline = 100 - yardline_100
        first_marker_downfield = (ball_on_yardline // 5) * 5 + 5
        yds_to_first_marker = first_marker_downfield - ball_on_yardline
        for y_relative in range(int(yds_to_first_marker), max_y_visible, 5):
            absolute_yardline = first_marker_downfield + (y_relative - yds_to_first_marker)
            if absolute_yardline > 50:
                label = 100 - absolute_yardline
            else:
                label = absolute_yardline
            if (pd.notna(yardline_100) and y_relative == yardline_100) or \
               (pd.notna(ydstogo) and y_relative == ydstogo):
                continue
                
            ax.axhline(y_relative, color='white', linestyle='-', alpha=0.5)
            ax.text(-24, y_relative + 0.5, str(label), color='white', fontsize=10)
            
    # Draw hash marks
    for y in np.arange(1, max_y_visible, 1):
        ax.plot([-9, -8], [y, y], color='white', alpha=0.5) # Left hash
        ax.plot([8, 9], [y, y], color='white', alpha=0.5)   # Right hash
        
    # Draw O-line
    ol_x = [-4, -2, 0, 2, 4]  # LT, LG, C, RG, RT
    ol_y = [0, 0, 0, 0, 0]
    ax.plot(ol_x, ol_y, 'o', color='white', markersize=10, label='Offensive Line')

    ax.set_xticks([])
    ax.set_yticks([])

def get_start_position(position, pass_location, formation):
    if position == 'RB' and 'EMPTY' in str(formation).upper():
        position = 'WR'

    if pd.isna(pass_location) or pass_location == 'middle':
        location_side = 'right'
    else:
        location_side = pass_location
        
    # Determine backfield depth based on formation
    if 'SHOTGUN' in str(formation).upper():
        backfield_y = -5
    elif 'SINGLEBACK' in str(formation).upper() or 'I_FORM' in str(formation).upper():
        backfield_y = -5 # Tailback depth for I_FORM and SINGLEBACK
    else:
        backfield_y = -5 # Default to shotgun depth

    # RB (Running Back)
    if position == 'RB':
        if 'I_FORM' in str(formation).upper() or 'SINGLEBACK' in str(formation).upper():
            return (0, backfield_y) # Tailback slot (0, -5)
        
        # Line up opposite the play direction in Shotgun
        if 'SHOTGUN' in str(formation).upper():
            if location_side == 'left':
                return (2, backfield_y) # Start offset RIGHT
            else:
                # If run is 'right' or 'middle', start offset LEFT
                return (-2, backfield_y) # Start offset LEFT

        # Starts in the backfield (Default for non-shotgun/I-form)
        if location_side == 'left':
            return (-2, backfield_y) # Offset left
        else:
            return (2, backfield_y)  # Offset right
        
    # TE (Tight End)
    elif position == 'TE':
        if location_side == 'left':
            return (-6, -0.5) # Left side
        else:
            return (6, -0.5)  # Right side
            
    # WR (Wide Receiver)
    elif position == 'WR':
        if location_side == 'left':
            return (-18, -0.5) # Wide left
        else:
            return (18, -0.5)  # Wide right
            
    # Default (if unknown position)
    else:
        return (0, 0)

def get_route_path(route_name, start_pos, position, location, air_yards):
    if pd.isna(route_name): route_name = "UNKNOWN"
    route_key = route_name.upper()
    
    start_x, start_y = start_pos
    is_left_side = start_x < 0
    if pd.isna(air_yards):
        if route_key == 'SCREEN': air_yards = -2 
        else: air_yards = 5 # Default 5-yard "unknown" route
    
    y = air_yards # `y` is our target depth

    if route_key == 'SCREEN' and position == 'RB':
        if location == 'left':
            relative_path = [(0, 1), (-5, y)]
        else:
            relative_path = [(0, 1), (5, y)]

    else:
        # Route definitions are now functions (lambda)
        ROUTE_DEFINITIONS = {
            'GO':       lambda y: [(0, y*0.5), (0, y)],
            'FADE':     lambda y: [(1, y*0.5), (3, y)],
            'OUT':      lambda y: [(0, y*0.8), (0, y), (5, y)], 
            'IN':       lambda y: [(0, y*0.8), (0, y), (-5, y)],
            'HITCH':    lambda y: [(0, y), (0, y-2)],
            'CURL':     lambda y: [(0, y), (0, y+2), (0, y), (-2, y)],
            'SLANT':    lambda _: [(0, 3), (-3, 6)], 
            'FLAT':     lambda _: [(3, 1), (5, 1)],
            'SCREEN':   lambda _: [(-3, 0), (-5, -2)], # WR Screen
            'WHEEL':    lambda _: [(3, 1), (5, 3), (5, 8), (3, 12), (0, 15)],
        }
        
        route_func = ROUTE_DEFINITIONS.get(route_key, lambda y: [(0, y*0.5), (1, y)]) # Default "UNKNOWN"
        relative_path = route_func(y) 

    if is_left_side and not (route_key == 'SCREEN' and position == 'RB'):
        mirror_routes = ['OUT', 'FLAT', 'IN', 'SLANT', 'FADE', 'CURL', 'SCREEN'] 
        if route_key in mirror_routes:
            relative_path = [(-x, y) for x, y in relative_path]

    absolute_path = [
        (start_x + rel_x, start_y + rel_y) 
        for rel_x, rel_y in relative_path
    ]
    
    return absolute_path

def get_run_path(run_location, run_gap, start_pos):
    target_x = 0 
    
    if run_location == 'middle':
        target_x = 0
    elif run_location == 'left':
        if run_gap == 'guard': target_x = -1
        elif run_gap == 'tackle': target_x = -3
        elif run_gap == 'end': target_x = -5
        else: target_x = -3
    elif run_location == 'right':
        if run_gap == 'guard': target_x = 1
        elif run_gap == 'tackle': target_x = 3
        elif run_gap == 'end': target_x = 5
        else: target_x = 3
            
    path_points = [
        (target_x, 0.5), # Hit the hole
        (target_x, 5)    # Run 5 yards
    ]
    return path_points

def parse_personnel(personnel_str):
    counts = {'RB': 0, 'TE': 0, 'WR': 0}
    if pd.isna(personnel_str):
        return counts
        
    personnel_str = personnel_str.replace('"', '')
    parts = personnel_str.split(',')
    
    for part in parts:
        part = part.strip()
        pieces = part.split(' ')
        if len(pieces) == 2:
            try:
                count = int(pieces[0])
                pos = pieces[1].strip()
                if pos in counts:
                    counts[pos] = count
            except ValueError:
                continue 
    return counts

def get_default_alignments(personnel_counts, formation, play_type='pass', location=None):
    alignments = []
    
    # Determine Backfield Depth
    if 'SHOTGUN' in str(formation).upper():
        backfield_y = -5
    elif 'SINGLEBACK' in str(formation).upper() or 'I_FORM' in str(formation).upper():
        backfield_y = -5 # Tailback depth
    else:
        backfield_y = -5 # Default

    # Define Default Slots
    WR_SLOTS = [
        (-18, -0.5), # WR 1 (Left Wide)
        (18, -0.5),  # WR 2 (Right Wide)
        (-12, -0.5), # WR 3 (Left Slot)
        (12, -0.5)   # WR 4 (Right Slot)
    ]
    
    TE_SLOT_RIGHT = (6, -0.5)
    TE_SLOT_LEFT = (-6, -0.5)
    is_run = play_type == 'run'
    run_side = str(location).lower()

    if is_run and run_side == 'left':
        TE_SLOTS = [TE_SLOT_LEFT, TE_SLOT_RIGHT]
    elif is_run and run_side == 'right':
        TE_SLOTS = [TE_SLOT_RIGHT, TE_SLOT_LEFT]
    else:
        TE_SLOTS = [TE_SLOT_RIGHT, TE_SLOT_LEFT]
        
    OFFSET_RB_SLOTS = [
        (2, backfield_y),  # RB 1 (Right Offset)
        (-2, backfield_y) # RB 2 (Left Offset)
    ]
    I_FORM_RB_SLOTS = [
        (0, -3), # FB
        (0, -5)  # TB
    ]
    
    # Fill Slots
    is_empty = 'EMPTY' in str(formation).upper()
    is_iform = 'I_FORM' in str(formation).upper()
    is_singleback = 'SINGLEBACK' in str(formation).upper()
    
    available_wr_slots = WR_SLOTS.copy()
    available_te_slots = TE_SLOTS.copy()
    
    if is_iform:
        available_rb_slots = I_FORM_RB_SLOTS.copy()
    elif is_singleback:
        available_rb_slots = [(0, backfield_y)] # Use the (0, -5) slot
    else:
        available_rb_slots = OFFSET_RB_SLOTS.copy()

    # 1. Place TEs
    for _ in range(personnel_counts.get('TE', 0)):
        if available_te_slots:
            slot = available_te_slots.pop(0) 
            alignments.append(('TE', slot))
            if slot in available_wr_slots:
                available_wr_slots.remove(slot)
                
    # 2. Place WRs
    for _ in range(personnel_counts.get('WR', 0)):
        if available_wr_slots:
            slot = available_wr_slots.pop(0)
            alignments.append(('WR', slot))
            if slot in available_te_slots:
                available_te_slots.remove(slot)

    # 3. Place RBs
    for _ in range(personnel_counts.get('RB', 0)):
        if is_empty:
            if available_wr_slots:
                slot = available_wr_slots.pop(0)
                alignments.append(('RB', slot))
            elif available_te_slots:
                slot = available_te_slots.pop(0)
                alignments.append(('RB', slot))
        else:
            if available_rb_slots:
                slot = available_rb_slots.pop(0)
                alignments.append(('RB', slot))
            else:
                alignments.append(('RB', (-2, backfield_y))) 
                
    return alignments


def visualize_play(game_id, play_id):
    if not os.path.exists(CSV_FILE):
        print(f"Error: File not found: {CSV_FILE}")
        print(f"Please make sure '{CSV_FILE}' is in the same directory.")
        return
        
    try:
        df = pd.read_csv(CSV_FILE, low_memory=False)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    play_matches = df[(df['game_id'] == game_id) & (df['play_id'] == play_id)]
    
    if play_matches.empty:
        print(f"Error: Play not found with:")
        print(f"  game_id: {game_id}")
        print(f"  play_id: {play_id}")
        other_ids = df[['game_id', 'play_id']].head(5).to_dict('records')
        print(f"Try one of these: {other_ids}")
        return
        
    play = play_matches.iloc[0]
    
    if len(play_matches) > 1:
        print(f"Warning: Found {len(play_matches)} duplicate plays for game {game_id}, play {play_id}.")
        print(f"Displaying the first one.")
        
    formation = play['offense_formation']
    personnel = play['offense_personnel']
    position = play['involved_player_position'] 
    
    try:
        # Use .loc to avoid potential Series/DataFrame ambiguity if data is bad
        down = play.loc['down']
        ydstogo = play.loc['ydstogo']
        yardline_100 = play.loc['yardline_100']
        down_str = f"{int(down)} & {int(ydstogo)}"
        yardline_str = f"{int(yardline_100)} yds to EZ"
    except (KeyError, ValueError, TypeError):
        print(f"Warning: Could not find or read 'down', 'ydstogo', or 'yardline_100' columns.")
        print(f"Please make sure your {CSV_FILE} file has these columns.")
        down_str = "Down: ?"
        yardline_str = "Ball: ?"
        ydstogo = None
        yardline_100 = None
    
    play_type = ''
    player_name = ''
    plot_label = ''
    path_info_str = ''
    path = []
    
    # Check if it's a pass play
    if pd.notna(play['receiver']):
        play_type = 'pass'
        player_name = play['receiver']
        route = play['route']
        location = play['pass_location'] 
        air_yards = play['air_yards']    
        plot_label = f'Targeted Receiver ({position})'
        path_info_str = f"Route: {str(route).upper()} ({air_yards} yds)"
        
        start_pos = get_start_position(position, location, formation)
        path = get_route_path(route, start_pos, position, location, air_yards)
        
    # Check if it's a run play
    elif pd.notna(play['rusher']):
        play_type = 'run'
        player_name = play['rusher']
        location = play['run_location'] 
        run_gap = play['run_gap']
        plot_label = f'Rusher ({position})'
        path_info_str = f"Run: {str(location).capitalize()} ({str(run_gap).capitalize()})"
        
        start_pos = get_start_position(position, location, formation)
        path = get_run_path(location, run_gap, start_pos)
        
    else:
        print(f"Warning: Play {play_id} is not a run or pass (no rusher or receiver). Skipping path.")
        start_pos = (0, -1) 
        plot_label = 'Unknown Play'

    print("\n" + "="*30)
    print(f"{game_id} / {play_id}")
    print(f"  > Situation: {down_str} | {yardline_str}")
    print(f"  > Formation Found: {formation}")
    print(f"  > Personnel Found: {personnel}")
    print(f"  > Play Type: {play_type}")
    print(f"  > Involved Player: {player_name} ({position})")
    print("="*30 + "\n")

    fig, ax = plt.subplots(figsize=(7, 10))
    fig.patch.set_facecolor('#F0F0F0') 
    
    # Draw the field first, passing situational data
    draw_field(ax, ydstogo, yardline_100)
    
    # Determine QB position based on formation
    formation_str = str(formation).upper()
    if 'SHOTGUN' in formation_str:
        qb_pos = (0, -5)
        qb_label = 'QB (Shotgun)'
    elif 'SINGLEBACK' in formation_str or 'I_FORM' in formation_str:
        qb_pos = (0, -1) # Under Center
        qb_label = 'QB (Under Center)'
    else:
        qb_pos = (0, -1) # Default to under center
        qb_label = 'QB (Reference)'
    
    # Plot QB
    ax.plot(qb_pos[0], qb_pos[1], 'o', color='yellow', markersize=12, label=qb_label)
    
    personnel_counts = parse_personnel(personnel)
    
    # Subtract the targeted player from the count
    if position in personnel_counts:
        personnel_counts[position] -= 1
    
    default_players = get_default_alignments(personnel_counts, formation, play_type, location)
    
    has_ghost_label = False
    for pos, (x, y) in default_players:
        if not has_ghost_label:
            ax.plot(x, y, 'o', color='white', markersize=10, alpha=0.7, label='Other Receivers')
            has_ghost_label = True
        else:
            ax.plot(x, y, 'o', color='white', markersize=10, alpha=0.7)
    
    # Plot the targeted player (Rusher or Receiver)
    start_x, start_y = start_pos
    ax.plot(start_x, start_y, 'o', color='cyan', markersize=12, label=plot_label)

    # Plot the Path (Route or Run)
    if path:
        full_path_x = [start_x] + [x for x, y in path]
        full_path_y = [start_y] + [y for x, y in path]
        
        ax.plot(full_path_x, full_path_y, '-', color='cyan', linewidth=3)
        
        ax.arrow(full_path_x[-2], full_path_y[-2], 
                 full_path_x[-1] - full_path_x[-2], 
                 full_path_y[-1] - full_path_y[-2],
                 head_width=1, head_length=1, fc='cyan', ec='cyan', length_includes_head=True)

    title_text = (
        f"Game: {game_id} | Play: {play_id}\n"
        f"{down_str} | {yardline_str}\n" 
        f"Player: {player_name}\n"
        f"Position: {position} | {path_info_str}\n" 
        f"Formation: {formation} | Personnel: {personnel}"
    )
    ax.set_title(title_text, fontsize=12)
    
    # Re-order the legend to be more logical
    handles, labels = ax.get_legend_handles_labels()
    
    # Filter out duplicate labels (e.g., if endzone/1st down aren't drawn)
    unique_labels = {}
    for h, l in zip(handles, labels):
        if l not in unique_labels:
            unique_labels[l] = h
            
    # Re-build handles and labels
    handles = unique_labels.values()
    labels = unique_labels.keys()
    
    ax.legend(handles=handles, labels=labels, loc='lower left')
    
    print(f"\nDisplaying visualization for Game: {game_id}, Play: {play_id}")
    print(f"To see a different play, change the 'GAME_ID_TO_VISUALIZE' and 'PLAY_ID_TO_VISUALIZE' variables.")
    
    plt.show()

if __name__ == "__main__":
    visualize_play(GAME_ID_TO_VISUALIZE, PLAY_ID_TO_VISUALIZE)

