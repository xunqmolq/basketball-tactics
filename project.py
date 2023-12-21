import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image


def load_players(filename):
  players = []
  with open(filename, 'r') as file:
    next(file)
    for line in file:
      player = line.split(',')[0].strip()
      players.append(player)
  return players


class PlayerSelectionApp:

  def __init__(self, root):
    self.root = root
    self.root.title("Basketball Tactics Selection")

    self.players_left = load_players('team-first.txt')
    self.players_right = load_players('team-second.txt')

    self.left_frame = tk.Frame(root)
    self.left_frame.grid(row=0, column=0, padx=10, pady=10)

    self.right_frame = tk.Frame(root)
    self.right_frame.grid(row=0, column=1, padx=10, pady=10)

    self.create_position_fields(self.left_frame, self.players_left,
                                "Your Team")
    self.create_position_fields(self.right_frame, self.players_right,
                                "Opponent's Team")

    self.tactic_button = tk.Button(root,
                                   text="Show best tactic",
                                   command=self.tactic)
    self.tactic_button.grid(row=1, columnspan=2, pady=10)


  def create_position_fields(self, frame, players, side):
    label = tk.Label(frame, text=f"Select Player ({side})")
    label.grid(row=0, column=0, columnspan=2)

    for i, position in enumerate(["PG", "SG", "SF", "PF", "C"]):
      position_label = tk.Label(frame, text=position)
      position_label.grid(row=i + 1, column=0, pady=5)

      player_var = tk.StringVar()
      player_combobox = ttk.Combobox(frame,
                                     textvariable=player_var,
                                     values=players)
      player_combobox.grid(row=i + 1, column=1, pady=5)

      def validate_selection(*args):
        selected_player = player_var.get()
        if selected_player:
          for other_position in range(1, 6):
            if other_position != i + 1:
              other_combobox = getattr(
                  self, f"{side.lower()}_combobox_{other_position}")
              if other_combobox.get() == selected_player:
                player_var.set("")
                messagebox.showerror("Error", "Player already selected in another position!")

      player_var.trace_add('write', validate_selection)
      setattr(self, f"{side.lower()}_combobox_{i + 1}", player_combobox)

  def tactic(self):
    left_selected_players = self.get_selected_players("Your Team")
    right_selected_players = self.get_selected_players("Opponent's Team")

    left_team = self.list_selected_players(left_selected_players,
                                           'team-first.txt')
    right_team = self.list_selected_players(right_selected_players,
                                            'team-second.txt')
    grades = []
    for i in range(5):
      your_player = left_team[i]
      opp_player = right_team[i]
      grade = opp_grade(player_efficiency(your_player[3:]),
                        player_efficiency(opp_player[3:]), your_player[1:3],
                        opp_player[1:3])
      grades.append(grade)
    final_grade = sum(grades) / len(grades)
    self.open_images(round(final_grade * 10))

  def open_images(self, grade):
    try:
      reverse_list = list(range(1,10))
      offense_image = f"offense-{abs(grade)}.jpg"
      defense_image = f"defense-{reverse_list[-abs(grade)]}.jpg"

      offense = Image.open(offense_image)
      defense = Image.open(defense_image)

      width1, height1 = offense.size
      width2, height2 = defense.size

      combined_image = Image.new('RGB', (width1 + width2, max(height1, height2)))

      combined_image.paste(offense, (0, 0))

      combined_image.paste(defense, (width1, 0))

      combined_image.show()
    except Exception as e:
      messagebox.showerror("Error",
                           f"An error occurred while opening the images: {e}")


  def get_selected_players(self, side):
    selected_players = []
    for i in range(1, 6):
      player_combobox = getattr(self, f"{side.lower()}_combobox_{i}")
      selected_player = player_combobox.get()
      if selected_player:
        selected_players.append(selected_player)
    return selected_players

  def list_selected_players(self, players, filename):
    list_players_and_stats = []
    for player in players:
      with open(filename, 'r') as file:
        next(file)
        for line in file:
          if player in line:
            data = line.strip().split(', ')
            list_players_and_stats.append(data)
    return list_players_and_stats


def player_efficiency(stats):
  eff = float(stats[0]) + float(stats[7]) + float(stats[8]) + float(
      stats[9]) + float(stats[10]) - (
          (float(stats[1]) - float(stats[2])) +
          (float(stats[3]) - float(stats[4])) +
          (float(stats[5]) - float(stats[6])) + float(stats[11]))
  return eff


def opp_grade(player1_eff, player2_eff, players1_biol, players2_biol):
  bmi_player1 = float(players1_biol[1]) / (float(players1_biol[0]) * 0.01)**2
  bmi_player2 = float(players2_biol[1]) / (float(players2_biol[0]) * 0.01)**2
  physique_diff = bmi_player1 - bmi_player2
  opp_grade = player1_eff - player2_eff + physique_diff
  grade_normal = opp_grade / abs(opp_grade + 1)
  if grade_normal >= 0:
    return grade_normal
  else:
    return -1 + (grade_normal % 1)


def main():
  root = tk.Tk()
  app = PlayerSelectionApp(root)
  root.mainloop()


if __name__ == "__main__":
  main()
