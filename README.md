# Tank Battle - GP Assignment 2

A 2-player tank battle game with realistic bullet physics and independent turret rotation.

## Features

- **HUD System**: Health bars displayed above tanks, kill counter, speed boost timer
- **Independent Turret Rotation**: Tank body and turret rotate separately
- **Bullet Reflection Physics**: Bullets bounce off walls with realistic reflection angles
- **Health System**: Each tank has 3 health points
- **Power-up System**: Collectible items that restore health or boost speed
- **Multiple Maps**: 6 different maps with unique layouts, randomly selected each game
- **Particle Effects**: Explosion effects when tanks are destroyed
- **Sound Effects**: Shooting, bouncing, and explosion sounds

## Running

```bash
python -m venv venv
venv\Scripts\Activate
pip install -r requirements.txt
python main.py
```

## Controls

### Player 1 (Blue Tank)
- **W**: Move forward
- **S**: Move backward
- **A**: Rotate tank body left
- **D**: Rotate tank body right
- **Q**: Rotate turret left
- **E**: Rotate turret right
- **SPACE** or **F**: Shoot

### Player 2 (Red Tank)
- **↑ (Up Arrow)**: Move forward
- **↓ (Down Arrow)**: Move backward
- **← (Left Arrow)**: Rotate tank body left
- **→ (Right Arrow)**: Rotate tank body right
- **,** (Comma): Rotate turret left
- **.** (Period): Rotate turret right
- **ENTER** or **M**: Shoot

### General Controls
- **ESC**: Exit game
- **Mouse Click**: Navigate menus

## Power-ups

The game features collectible power-up items that spawn randomly on the map every 10 seconds. Drive your tank over them to collect and gain advantages in battle.

### Available Power-ups

#### Health Restore (Red +)
- **Appearance**: Red circle with a white "+" symbol
- **Effect**: Instantly restores 1 health point
- **Usage**: Collect when your health is low to stay in the fight
- **Note**: Cannot exceed maximum health (3 HP)

#### Speed Boost (Blue »)
- **Appearance**: Cyan/Blue circle with a "»" symbol
- **Effect**: Increases tank movement speed by 50% for 5 seconds
- **Usage**: Collect to chase enemies or escape dangerous situations
- **Display**: Active speed boost timer shown in the HUD
- **Stack**: Cannot stack multiple speed boosts; collecting a new one refreshes the duration

### Power-up Mechanics

- **Spawn Rate**: New power-ups spawn every 10 seconds
- **Spawn Location**: Random valid positions (not on walls or obstacles)
- **Visual Effects**: Power-ups have pulsing glow effects for visibility
- **Auto-Collection**: Simply drive your tank over a power-up to collect it
- **Strategic Value**: Use power-ups tactically to gain advantage over your opponent

## Maps

The game features 6 different maps, each with unique layouts and strategic challenges. A random map is selected each time you start a new game.

### Available Maps:

1. **Classic Maze**: Complex maze with multiple corridors and obstacles
2. **Arena**: Symmetrical arena with strategic pillars for cover
3. **Corridors**: Long pathways with tactical chokepoints
4. **Center Box**: Open field with a central fortified position
5. **Cross Pattern**: Asymmetric layout with cross-shaped walls
6. **Diagonal**: Diagonal wall creating unique bouncing angles

### Map Features:

- **Random Selection**: Each game starts with a randomly chosen map
- **HUD Display**: Current map name shown in the center of the HUD during gameplay
- **Variety**: Different layouts require different tactics and strategies
- **Replay Value**: Multiple maps provide fresh experiences in each session

## Physics Implementation

### Bullet Reflection Mechanics

The game implements realistic bullet reflection using axis-separated collision detection:

1. **Axis-Separated Movement**: The bullet moves along the X-axis and Y-axis independently in each frame update.

2. **Collision Detection**: After each axis movement, the bullet checks for collision with walls.

3. **Reflection Logic**:
   - **X-axis collision** (vertical walls): The horizontal velocity component is reversed (`velocity_x *= -1`)
   - **Y-axis collision** (horizontal walls): The vertical velocity component is reversed (`velocity_y *= -1`)

4. **Wall Penetration Prevention**: When a collision is detected, the bullet is pushed back to the wall's edge to prevent it from getting stuck inside the wall.

5. **Bounce Limit**: Bullets can bounce up to 10 times before being deactivated to prevent infinite bouncing.

6. **Visual Update**: After each bounce, the bullet sprite is rotated to match its new direction based on the updated velocity vector.

This approach creates realistic reflection angles where:
- The angle of incidence equals the angle of reflection
- Bullets maintain their speed after bouncing
- Complex trajectories can be created by bouncing off multiple walls

### Code Example
```python
def _check_bounce(self, walls, axis):
    for wall in walls:
        if self.rect.colliderect(wall):
            if axis == 'x':
                self.velocity_x *= -1  # Reflect on vertical wall
                # Push bullet out to prevent sticking
                if self.velocity_x > 0: 
                    self.rect.left = wall.right
                else: 
                    self.rect.right = wall.left
                self.x = self.rect.centerx
            elif axis == 'y':
                self.velocity_y *= -1  # Reflect on horizontal wall
                if self.velocity_y > 0: 
                    self.rect.top = wall.bottom
                else: 
                    self.rect.bottom = wall.top
                self.y = self.rect.centery
            
            self.bounces += 1
            self._update_rotation()  # Update sprite rotation
            return True
    return False
```

## Asset Sources

### Graphics
- **Tank and Barrel Sprites**: [Old School Tanks by Uto Pix Studio](https://uto-pix-studio.itch.io/old-school-tanks)

### Audio
- **Explosion Sound Effect**: [LordSonny](https://pixabay.com/users/lordsonny-38439655/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=161647) from [Pixabay](https://pixabay.com/sound-effects//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=161647)

- **Bullet Sound Effect**: [freesound_community](https://pixabay.com/users/freesound_community-46691455/?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=39872) from [Pixabay](https://pixabay.com/sound-effects//?utm_source=link-attribution&utm_medium=referral&utm_campaign=music&utm_content=39872)

## Game Rules

- Each tank starts with 3 health points
- Each bullet hit reduces health by 1
- When health reaches 0, the tank explodes and the round ends
- Power-ups spawn every 10 seconds at random locations
- Health power-ups restore 1 HP (max 3 HP)
- Speed boosts increase movement speed by 50% for 5 seconds
- Kills are tracked across rounds when pressing "PLAY AGAIN"
- Returning to main menu resets all scores
- Bullets can hit their owner only after bouncing off a wall
