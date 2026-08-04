"""
Pokémon TCG Battle Simulator
A simple turn-based card game engine with evolution, status effects, and energy management.
"""
from __future__ import annotations
import json, os, random, sys, time
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any

# ======== FILE PATHS ========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DECKS_FILE = os.path.join(BASE_DIR, "decks.json")
EFFECTS_FILE = os.path.join(BASE_DIR, "effects.json")
CARD_PROPERTIES_FILE = os.path.join(BASE_DIR, "card_properties.json")
POKEMON_STATS_FILE = os.path.join(BASE_DIR, "pokemon_stats.json")
MOVE_SETS_FILE = os.path.join(BASE_DIR, "move_sets.json")
PACKS_FILE = os.path.join(BASE_DIR, "packs.json")

ALLOWED_DECKS = set()

# ======== UTILITIES ========
def clear():
	"""Clear console screen (Windows/Unix compatible)."""
	os.system('cls' if os.name == 'nt' else 'clear')

def ask(prompt: str) -> str:
	"""Safely get user input with fallback."""
	try:
		return input(prompt)
	except EOFError:
		return ""

def flip() -> bool:
	"""Animated coin flip (50% chance). Returns True for heads."""
	frames = ['○', '●', '○', '●', '○', '●']
	print("\nFlipping coin", end='', flush=True)
	for frame in frames:
		print(f"\rFlipping coin: {frame}", end='', flush=True)
		time.sleep(0.15)
	result = random.random() < 0.5
	print(f"\rCoin flip: {'HEADS! ⚪' if result else 'TAILS! ⚫'}")
	return result

# ======== ENERGY DISPLAY HELPERS ========
def get_energy_emoji(energy_type: str) -> str:
	"""Map energy type to colored ball emoji."""
	energy_emojis = {
		"Water": "🔵",      # Blue ball
		"Fire": "🔴",       # Red ball
		"Grass": "🟢",      # Green heart (grass color)
		"Lightning": "⚡",   # Lightning (yellow equivalent)
		"Psychic": "🟣",    # Purple ball
		"Fighting": "🟤",   # Brown ball
		"Colorless": "⚪"   # White ball
	}
	return energy_emojis.get(energy_type, "⚪")

def format_energy_balls(energies: Dict[str, int]) -> str:
	"""Format attached energies as colored balls."""
	if not energies:
		return ""
	
	balls = []
	for energy_type, count in energies.items():
		emoji = get_energy_emoji(energy_type)
		balls.extend([emoji] * count)
	
	return " ".join(balls)

def show_pokemon_status(pokemon: Optional[PokemonCard], energies: Optional[Dict[str, int]] = None) -> str:
	"""Format Pokémon display with HP, status icons, retreat cost, and energy balls."""
	if not pokemon:
		return "No active Pokémon"
	
	status_icons = {
		"poison": "☠️", "paralyze": "⚡", "sleep": "💤",
		"confuse": "💫", "stiffen": "🛡️"
	}
	
	status_list = [
		f"{status_icons.get(eff, '❓')}{eff.upper()}"
		for eff, count in pokemon.status.items() if count > 0
	]
	status_txt = f" [{', '.join(status_list)}]" if status_list else ""
	
	energy_balls = format_energy_balls(energies) if energies else ""
	energy_txt = f" {energy_balls}" if energy_balls else ""
	
	return f"{pokemon.name}{energy_txt} HP:{pokemon.hp}/{pokemon.max_hp}{status_txt} [Retreat: {pokemon.retreat_cost}⚡]"

# ======== DATA CLASSES ========
@dataclass
class Card:
	"""Base card class."""
	name: str
	type: str
	rarity: str

@dataclass
class EnergyCard(Card):
	"""Energy card - provides cost payment."""
	pass

@dataclass
class TrainerCard(Card):
	"""Trainer card - special effects."""
	effect: str

@dataclass
class PokemonCard(Card):
	"""Pokémon card - battler with moves and status."""
	hp: int
	max_hp: int
	basic: bool
	weakness: Optional[str] = None
	resistance: Optional[str] = None
	retreat_cost: int = 1
	description: str = ""
	moves: List[Tuple[str, Tuple[str, int], int, Any]] = field(default_factory=list)
	status: Dict[str, int] = field(default_factory=dict)
	
	def is_affected_by(self, status_type: str) -> bool:
		"""Check if status is active (duration > 0)."""
		return self.status.get(status_type, 0) > 0
	
	def add_status(self, status_type: str, duration: int) -> None:
		"""Apply status, keeping highest duration if already active."""
		self.status[status_type] = max(duration, self.status.get(status_type, 0))
	
	def remove_status(self, status_type: str) -> None:
		"""Remove status effect."""
		self.status.pop(status_type, None)

@dataclass
class Player:
	"""Player state: deck, hand, bench, prizes, active Pokémon."""
	name: str
	deck: List[Card] = field(default_factory=list)
	hand: List[Card] = field(default_factory=list)
	prizes: List[Card] = field(default_factory=list)
	discard: List[Card] = field(default_factory=list)
	active: Optional[PokemonCard] = None
	bench: List[PokemonCard] = field(default_factory=list)
	energies: Dict[str, Dict[str, int]] = field(default_factory=dict)
	attached_this_turn: bool = False
	
	def can_attack(self) -> bool:
		"""Check if active can attack (not paralyzed/asleep)."""
		return (self.active is not None and 
				not self.active.is_affected_by("paralyze") and
				not self.active.is_affected_by("sleep"))

# ======== DATA LOADING ========
def load_json(path: str, key: str = None) -> Dict:
	"""Load and parse JSON file with optional key extraction."""
	if not os.path.exists(path):
		print(f"[ERRO] {path} not found")
		sys.exit(1)
	with open(path, "r", encoding="utf-8") as f:
		data = json.load(f)
	return data.get(key, data) if key else data

EFFECTS = load_json(EFFECTS_FILE)
CARD_PROPERTIES = load_json(CARD_PROPERTIES_FILE, "pokemon_properties")
POKEMON_STATS = load_json(POKEMON_STATS_FILE, "pokemon_stats")

def load_decks(path: str) -> List[dict]:
	"""Load deck definitions, apply filters."""
	data = load_json(path)
	decks = data.get("decks", [])
	if ALLOWED_DECKS:
		decks = [d for d in decks if d.get("name") in ALLOWED_DECKS]
	if not decks:
		print("[ERRO] No decks available after filter.")
		sys.exit(1)
	return decks

def is_energy(name: str, ctype: str, rarity: str) -> bool:
	"""Detect if card is an Energy card."""
	return rarity.lower() == "energy" or "energy" in name.lower()

def get_moves_for_card(name: str) -> List:
	"""Extract all moves from move_sets.json (simple approach: all moves available)."""
	try:
		move_data = load_json(MOVE_SETS_FILE)
		moves = []
		for type_moves in move_data.get("moves", {}).values():
			for move_name, move_info in type_moves.items():
				cost_type = next(iter(move_info.get("cost", {})))
				cost_amount = move_info["cost"][cost_type]
				moves.append((
					move_name,
					(cost_type, cost_amount),
					move_info.get("base_damage", 0),
					move_info.get("effect", {}).get("type", [])
				))
		return moves
	except Exception as e:
		print(f"Warning: Could not load moves for {name}: {e}")
		return []

def build_deck(defn: dict) -> List[Card]:
	"""Build Card objects from deck definition."""
	out = []
	for item in defn.get("cards", []):
		qty = int(item.get("quantity", 1))
		name = item.get("card")
		ctype = item.get("type", "").replace(" E", "").strip() or "Colorless"
		rarity = item.get("rarity", "Common")

		# Energy cards
		if is_energy(name, ctype, rarity):
			out += [EnergyCard(name, ctype, "Energy") for _ in range(qty)]
			continue

		# Trainer cards
		if rarity.lower() == "trainer" or ctype in ("T", "Trainer"):
			key = name.lower().replace(" ", "_")
			effect_cfg = EFFECTS.get("trainer_effects", {}).get(key, {})
			effect_desc = effect_cfg.get("description", CARD_PROPERTIES.get(name, {}).get("description", ""))
			out += [TrainerCard(name, ctype, rarity, effect_desc) for _ in range(qty)]
			continue

		# Pokémon cards
		stats = POKEMON_STATS.get(name, {})
		props = CARD_PROPERTIES.get(name, {})
		moves = get_moves_for_card(name)
		
		hp = int(stats.get("hp", props.get("hp", 50)))
		for _ in range(qty):
			out.append(PokemonCard(
				name, ctype, rarity,
				hp=hp, max_hp=hp,
				basic=bool(props.get("basic", True)),
				weakness=stats.get("weakness"),
				resistance=stats.get("resistance"),
				retreat_cost=int(props.get("retreat_cost", 1)),
				description=props.get("description", ""),
				moves=moves
			))
	
	random.shuffle(out)
	return out

# ======== GAME SETUP ========
def draw(p: Player, n: int) -> None:
	"""Draw n cards. Raise error if deck empty."""
	for _ in range(n):
		if not p.deck:
			raise RuntimeError(f"{p.name} deck-out!")
		p.hand.append(p.deck.pop())

def setup_player(name: str, defn: dict) -> Player:
	"""Build player with initial hand, active, bench, and prizes."""
	deck = build_deck(defn)
	p = Player(name=name, deck=deck)
	
	# Mulligan until hand has basic Pokémon
	while True:
		p.hand.clear()
		p.deck = deck.copy()
		random.shuffle(p.deck)
		draw(p, 7)
		basics = [c for c in p.hand if isinstance(c, PokemonCard) and c.basic]
		if basics:
			break
	
	# Set active and bench
	p.active = basics[0]
	p.hand.remove(p.active)
	for c in [x for x in p.hand if isinstance(x, PokemonCard) and x.basic][:5]:
		p.bench.append(c)
		p.hand.remove(c)
	
	# Set up prizes
	p.prizes = [p.deck.pop() for _ in range(4)]
	return p

# ======== GAME MECHANICS ========
def can_pay(cost: Tuple[str, int], pool: Dict[str, int]) -> bool:
	"""Check if energy pool can pay a cost."""
	energy_type, needed = cost
	if energy_type == "Colorless":
		return sum(pool.values()) >= needed
	return pool.get(energy_type, 0) >= needed

def can_retreat(p: Player) -> bool:
	"""Check if player can retreat (have benched Pokémon and enough energy)."""
	if not p.active or not p.bench:
		return False
	pool = p.energies.get(p.active.name, {})
	return sum(pool.values()) >= p.active.retreat_cost

def perform_retreat(p: Player, bench_idx: int) -> bool:
	"""Retreat active to bench, swap with selected benched Pokémon."""
	if not can_retreat(p):
		return False
	
	# Consume retreat energy
	pool = p.energies.get(p.active.name, {})
	cost = p.active.retreat_cost
	for energy_type in list(pool.keys()):
		if cost <= 0:
			break
		consumed = min(pool[energy_type], cost)
		pool[energy_type] -= consumed
		cost -= consumed
		if pool[energy_type] == 0:
			del pool[energy_type]
	
	# Swap
	old_active = p.active
	p.active = p.bench.pop(bench_idx)
	p.bench.append(old_active)
	print(f"{p.name} retreated {old_active.name} for {p.active.name}")
	return True

def poison_check(p: Player) -> None:
	"""Apply poison damage and decrement counter."""
	if not p.active or not p.active.is_affected_by("poison"):
		return
	
	damage = 10
	prev_hp = p.active.hp
	p.active.hp = max(0, p.active.hp - damage)
	
	print(f"\n☠️ Poison on {p.name}'s {p.active.name}: {prev_hp} → {p.active.hp}/{p.active.max_hp}")
	
	p.active.status["poison"] -= 1
	if p.active.status["poison"] <= 0:
		p.active.remove_status("poison")
		print(f"✨ {p.active.name} is no longer poisoned!")

def decay_paralyze(p: Player) -> None:
	"""Decrement paralyze counter."""
	if p.active and p.active.is_affected_by("paralyze"):
		p.active.status["paralyze"] -= 1
		if p.active.status["paralyze"] <= 0:
			p.active.remove_status("paralyze")

# ======== EFFECTS ENGINE ========
MOVE_DEFAULT_EFFECTS = {
	"poison sting": ["poison_sting"],
	"bubblebeam": ["paralyze_on_heads"],
	"star freeze": ["paralyze_on_heads"],
	"flail": ["flail_10x_damage_counters"],
	"recover": ["recover_full_discard1"]
}

def apply_effect_id(eid: str, atk: PokemonCard, defpk: PokemonCard,
					atk_pool: Dict[str, int], atk_player: Player) -> int:
	"""Apply move effect by ID from effects.json. Returns damage delta or 0."""
	effect = (EFFECTS.get("move_effects", {}).get(eid.lower()) or 
			 EFFECTS.get("effect_templates", {}).get(eid.lower()))
	
	if not effect:
		# Fallback for poison_sting
		if eid == "poison_sting" and flip():
			defpk.add_status("poison", 3)
			print(f"☠️ {defpk.name} was poisoned for 3 turns!")
		return 0
	
	effect_kind = effect.get("kind", "").lower()
	
	# Status effect on coin flip
	if effect_kind == "status_on_heads":
		if flip():
			status = effect.get("status", "").lower()
			duration = int(effect.get("duration", 1))
			defpk.add_status(status, duration)
			print(f"✨ {defpk.name} now has {status}!")
		return 0
	
	# Poison effect (alternative form)
	if effect_kind == "poison_effect":
		if effect.get("chance") != "flip" or flip():
			defpk.add_status("poison", int(effect.get("duration", 3)))
			print(f"☠️ {defpk.name} poisoned!")
		return 0
	
	# Healing
	if effect_kind == "heal_attacker":
		amount = int(effect.get("amount", 0))
		healed = min(amount, atk.max_hp - atk.hp)
		atk.hp += healed
		if healed > 0:
			print(f"💚 Healed {healed}")
		return 0
	
	# Recovery (discard energy)
	if effect_kind == "recover_full_discard":
		if sum(atk_pool.values()) >= 1:
			energy_type = next(iter(atk_pool))
			atk_pool[energy_type] -= 1
			if atk_pool[energy_type] <= 0:
				del atk_pool[energy_type]
			atk.hp = atk.max_hp
			print(f"💚 Fully recovered!")
		return 0
	
	# Shield
	if effect_kind == "self_shield_on_heads":
		if flip():
			atk.add_status("stiffen", int(effect.get("turns", 2)))
			print("🛡️ Stiffen active!")
		return 0
	
	return 0

# ======== COMBAT ========
def wmult(atk: PokemonCard, defpk: PokemonCard) -> float:
	"""Weakness multiplier (2x or 1x)."""
	return 2.0 if defpk.weakness and atk.type == defpk.weakness else 1.0

def rsub(atk: PokemonCard, defpk: PokemonCard) -> int:
	"""Resistance damage reduction (30 or 0)."""
	return 30 if defpk.resistance and atk.type == defpk.resistance else 0

def list_moves(pk: PokemonCard) -> List[str]:
	"""Format move list for display."""
	return [f"{i}) {n} ({c} {t}) [{d} dmg]"
			for i, (n, (t, c), d, _) in enumerate(pk.moves, 1)]

def perform_attack(att: Player, deff: Player) -> None:
	"""Execute attack: check conditions, apply effects, deal damage."""
	if not att.active or not deff.active:
		return
	
	atk, tgt = att.active, deff.active
	
	# Stiffen protection
	if tgt.status.get("stiffen", 0) > 0:
		print(f"🛡️ {deff.name}'s {tgt.name} is protected (Stiffen)!")
		tgt.status["stiffen"] -= 1
		if tgt.status["stiffen"] <= 0:
			tgt.remove_status("stiffen")
		return
	
	# Paralyze blocks attack
	if atk.status.get("paralyze", 0) > 0:
		print(f"⚡ {att.name}'s {atk.name} is paralyzed and cannot attack!")
		return
	
	# Check playable moves
	pool = att.energies.get(atk.name, {})
	playable = [i for i, mv in enumerate(atk.moves) if can_pay(mv[1], pool)]
	if not playable:
		print(f"❌ {att.name} has no moves with sufficient energy!")
		return
	
	# Choose move
	if att.name == "Player":
		print("\nChoose move:")
		for line in list_moves(atk):
			print(f"  {line}")
		try:
			idx = int(ask("Move #: ")) - 1
			if idx not in playable:
				idx = playable[0]
		except ValueError:
			idx = playable[0]
	else:
		idx = playable[0]
	
	# Execute move
	mname, cost, base, eff = atk.moves[idx]
	cur = base
	effect_ids = eff if isinstance(eff, list) else MOVE_DEFAULT_EFFECTS.get(mname.lower(), [])
	for eid in effect_ids:
		apply_effect_id(eid, atk, tgt, pool, att)
	
	# Calculate damage
	dmg = max(0, int(cur * wmult(atk, tgt)) - rsub(atk, tgt))
	tgt.hp = max(0, tgt.hp - dmg)
	
	print(f"\n⚔️ {att.name}'s {atk.name} used {mname}")
	print(f"💥 Damage: {dmg} | HP: {tgt.hp}/{tgt.max_hp}")
	if tgt.resistance and atk.type == tgt.resistance:
		print(f"💪 Resistance reduced damage by 30!")
	if tgt.hp > 0:
		print(f"Status: {show_pokemon_status(tgt)}")
	
	# KO handling
	if tgt.hp <= 0:
		print(f"💀 {tgt.name} was KO'd!")
		deff.discard.append(tgt)
		deff.active = None
		if deff.bench:
			deff.active = deff.bench.pop(0)
			print(f"➜ {deff.name} promoted {deff.active.name}.")
		if att.prizes:
			att.hand.append(att.prizes.pop())
			print(f"🏆 Prize! {len(att.prizes)} remaining.")

# ======== TRAINER EFFECTS ========
def apply_trainer_effect(card: TrainerCard, player: Player, opponent: Player) -> bool:
	"""Apply trainer card effect. Return True if successful."""
	
	effect = EFFECTS.get("trainer_effects", {}).get(card.name.lower().replace(" ", "_"))
	if not effect:
		print(f"❓ {card.name} has no defined effect")
		return False
	
	etype = effect.get("type", "")
	
	# Draw
	if etype == "draw":
		try:
			draw(player, effect.get("cards", 0))
			print(f"✨ {card.name}: +{effect.get('cards')} cards")
			return True
		except RuntimeError as e:
			print(f"❌ {e}")
			return False
	
	# Heal
	elif etype == "heal":
		if not player.active:
			print("❌ No active Pokémon to heal")
			return False
		
		# Check energy cost
		if "cost" in effect:
			cost = effect["cost"]
			if cost.get("type") == "discard_energy":
				pool = player.energies.get(player.active.name, {})
				if sum(pool.values()) < cost.get("amount", 1):
					print(f"❌ {card.name} requires discarding energy")
					return False
				# Discard
				energy_type = next(iter(pool))
				pool[energy_type] -= cost.get("amount", 1)
				if pool[energy_type] <= 0:
					del pool[energy_type]
		
		# Heal
		healed = min(effect.get("amount", 0), player.active.max_hp - player.active.hp)
		player.active.hp += healed
		print(f"💚 {card.name}: +{healed} HP")
		return True
	
	# Swap
	elif etype == "swap":
		if effect.get("from") == "active":
			if not player.bench:
				print("❌ No benched Pokémon")
				return False
			idx = choose_from([b.name for b in player.bench], "Switch with:")
			if idx >= 0:
				new = player.bench.pop(idx)
				player.bench.insert(0, player.active)
				player.active = new
				print(f"➜ {player.active.name} is active")
				return True
		
		elif effect.get("from") == "opponent_active":
			if not opponent.bench:
				print("❌ Opponent has no benched Pokémon")
				return False
			idx = choose_from([b.name for b in opponent.bench], "Force switch:")
			if idx >= 0:
				new = opponent.bench.pop(idx)
				opponent.bench.insert(0, opponent.active)
				opponent.active = new
				print(f"⚡ Opponent switched to {opponent.active.name}")
				return True
	
	return False

# ======== HAND MANAGEMENT ========
def play_card_from_hand(p: Player, o: Player, idx: int) -> None:
	"""Play card from hand: Energy (attach), Trainer (effect), or Pokémon (bench/evolve)."""
	if idx < 0 or idx >= len(p.hand):
		print("❌ Invalid card index")
		return
	
	card = p.hand[idx]
	
	# Energy card
	if isinstance(card, EnergyCard):
		if not p.active:
			print("❌ No active Pokémon")
			return
		if p.attached_this_turn:
			print("❌ Already attached Energy this turn")
			return
		p.hand.pop(idx)
		pool = p.energies.setdefault(p.active.name, {})
		pool[card.type] = pool.get(card.type, 0) + 1
		p.attached_this_turn = True
		print(f"⚡ Attached {card.type} Energy to {p.active.name}")
		return
	
	# Trainer card
	if isinstance(card, TrainerCard):
		if apply_trainer_effect(card, p, o):
			p.hand.pop(idx)
			p.discard.append(card)
		return
	
	# Pokémon card
	if isinstance(card, PokemonCard):
		props = CARD_PROPERTIES.get(card.name, {})
		evolves_from = props.get("evolves_from")
		
		# Evolution
		if p.active and evolves_from == p.active.name:
			p.hand.pop(idx)
			old_name = p.active.name
			energy_pool = p.energies.pop(old_name, {})
			prev_hp = p.active.hp
			p.discard.append(p.active)
			
			# New active with preserved energies
			card.hp = min(prev_hp, card.max_hp)
			p.active = card
			if energy_pool:
				p.energies[p.active.name] = energy_pool
			
			print(f"✨ Evolved to {p.active.name}!")
			return
		
		# Bench
		if len(p.bench) >= 5:
			print("❌ Bench is full")
			return
		p.hand.pop(idx)
		p.bench.append(card)
		print(f"📦 Benched {card.name}")
		return
	
	print("❌ Cannot play this card")

def choose_from(lst: List[str], title: str, cancel: str = "Cancel") -> int:
	"""Interactive choice from list. Return index or -1."""
	print(title)
	for i, x in enumerate(lst, 1):
		print(f"{i}) {x}")
	print(f"0) {cancel}")
	try:
		choice = int(ask("Choice: ")) - 1
		return choice if 0 <= choice < len(lst) else -1
	except ValueError:
		return -1

# ======== TURN FLOW ========
def take_turn(p: Player, o: Player) -> str:
	"""Execute player turn: draw, play cards, attack. Return 'win'/'lose'/'ok'."""
	print(f"\n{'='*50}")
	print(f"  {p.name}'s Turn")
	print(f"{'='*50}")
	
	# Show status with energy balls
	if p.active:
		p_energies = p.energies.get(p.active.name, {})
		print(f"\n{p.name}'s: {show_pokemon_status(p.active, p_energies)}")
	if o.active:
		o_energies = o.energies.get(o.active.name, {})
		print(f"{o.name}'s: {show_pokemon_status(o.active, o_energies)}")
	
	# Poison check
	poison_check(p)
	if p.active and p.active.hp <= 0:
		print(f"💀 {p.active.name} fainted from poison!")
		p.discard.append(p.active)
		p.active = p.bench.pop(0) if p.bench else None
		if not p.active:
			return "lose"
	
	# Draw
	try:
		draw(p, 1)
		print(f"🎴 Drew 1 card (Hand: {len(p.hand)})")
	except RuntimeError:
		return "lose"
	
	# Action loop
	p.attached_this_turn = False
	while True:
		if p.active:
			bench_names = [b.name for b in p.bench]
			p_energies = p.energies.get(p.active.name, {})
			energy_display = format_energy_balls(p_energies)
			active_display = f"{p.active.name} {energy_display}".strip()
			print(f"\n🎯 Active: {active_display} | Bench: {bench_names if bench_names else 'Empty'}")
		
		# Display hand properly
		if p.hand:
			print(f"🎴 Hand ({len(p.hand)}):")
			for i, c in enumerate(p.hand, 1):
				print(f"  {i}) {c.name}")
		else:
			print(f"🎴 Hand (0): Empty")
		
		print("\n━━━ Actions ━━━")
		print("1) Hand  — Play card")
		print("2) Retreat")
		print("3) Attack")
		print("4) Done")
		
		ch = ask("Action: ").strip()
		
		if ch == "1":
			if not p.hand:
				print("❌ Hand is empty")
				continue
			try:
				ci = int(ask("Card #: ")) - 1
				if 0 <= ci < len(p.hand):
					play_card_from_hand(p, o, ci)
			except ValueError:
				pass
			continue
		
		elif ch == "2":
			if not p.bench:
				print("❌ No benched Pokémon")
				continue
			if not can_retreat(p):
				print("❌ Not enough energy to retreat")
				continue
			for i, b in enumerate(p.bench, 1):
				print(f"{i}) {b.name} HP:{b.hp}/{b.max_hp}")
			try:
				ci = int(ask("Switch to: ")) - 1
				if 0 <= ci < len(p.bench):
					perform_retreat(p, ci)
			except ValueError:
				pass
			continue
		
		elif ch == "3":
			perform_attack(p, o)
			break
		
		elif ch == "4":
			break
		
		else:
			print("❌ Invalid action")
	
	decay_paralyze(p)
	
	# Win conditions
	if not o.active and not o.bench:
		print(f"\n🏆 {p.name} wins!")
		return "win"
	if not p.prizes:
		print(f"\n🏆 {p.name} wins!")
		return "win"
	return "ok"

# ======== MAIN LOOP ========
def choose_deck(decks: List[dict], title: str) -> dict:
	"""Deck selection menu."""
	while True:
		clear()
		print(title)
		for i, d in enumerate(decks, 1):
			types = ', '.join(d.get('types_used', ['?']))
			print(f"{i}) {d['name']} — {types}")
		try:
			idx = int(ask("\nDeck #: ")) - 1
			if 0 <= idx < len(decks):
				return decks[idx]
		except ValueError:
			pass

def main():
	"""Main game loop."""
	random.seed()
	decks = load_decks(DECKS_FILE)
	
	p_def = choose_deck(decks, "Choose your deck:")
	c_def = choose_deck(decks, "Choose opponent's deck:")
	
	player = setup_player("Player", p_def)
	cpu = setup_player("CPU", c_def)
	
	clear()
	print("🎮 POKÉMON TCG BATTLE START 🎮")
	print(f"Player: {player.active.name} | Bench: {[b.name for b in player.bench]}")
	print(f"CPU:    {cpu.active.name} | Bench: {[b.name for b in cpu.bench]}")
	ask("\n[Enter to begin]")
	
	cur, other = player, cpu
	turn_count = 0
	
	while True:
		turn_count += 1
		clear()
		print(f"  Turn {turn_count}")
		print(f"Prizes — Player: {len(player.prizes)} | CPU: {len(cpu.prizes)}")
		
		result = take_turn(cur, other)
		if result in ("win", "lose"):
			break
		
		cur, other = other, cur
		ask("\n[Enter next turn]")
	
	print(f"\n{'='*50}")
	print("GAME OVER")
	print(f"{'='*50}")

if __name__ == "__main__":
	main()
