from abc import ABC, abstractmethod
import random
import sys
import math

class Dado:
    @staticmethod
    def rolar(a=1,b=6): return random.randint(a,b)

def limpar_console():
    print("\n" * 50)
    
def gerar_status_base_aleatorio():
    return {
        "HP": Dado.rolar(8, 15),
        "ATK": Dado.rolar(8, 15),
        "DEF": Dado.rolar(8, 15),
        "SPD": Dado.rolar(8, 15)
    }

class Item:
    def __init__(self, nome): self.nome = nome

class PocaoCura(Item):
    def __init__(self): super().__init__("Poção de Cura")
    def usar(self, heroi, battle):
        cura = Dado.rolar(1, 12)
        curado = heroi.curar(cura)
        battle.registrar(f" {heroi.nome} usou {self.nome} e recuperou {curado} HP. ({heroi.vida}/{heroi.vida_max})", 'heal')
        return curado

class Inventario:
    def __init__(self): self.itens = []
    def adicionar(self, item): self.itens.append(item)
    def remover(self, item): self.itens.remove(item); return True
    def contar(self, item_class): 
        return sum(1 for item in self.itens if isinstance(item, item_class))
    def listar(self): return self.itens

def gerar_modificador_aleatorio(tipo):
    if tipo == 'ATK': return Dado.rolar(1, 10)
    if tipo in ('HP', 'DEF'): return Dado.rolar(1, 10)
    if tipo == 'SPD': return Dado.rolar(1, 15)
    return 0

class Equipamento(Item):
    def __init__(self, nome, slot, modificadores):
        self.modificadores = modificadores
        super().__init__(nome)
        self.slot = slot 
        
    def get_bonus_str(self):
        mod_str = []
        for stat, val in self.modificadores.items():
            if val > 0: mod_str.append(f"+{val} {stat}")
        return f"({', '.join(mod_str)})"

class Arma(Equipamento):
    def __init__(self, atk_bonus=None, nome_base="Arma"):
        atk = atk_bonus if atk_bonus is not None else gerar_modificador_aleatorio('ATK')
        mod = {'ATK': atk, 'DEF': 0, 'HP': 0, 'SPD': 0}
        
        mod_str = []
        for stat, val in mod.items():
            if val > 0: mod_str.append(f"+{val} {stat}")
        bonus_display = f"({', '.join(mod_str)})"
        
        if atk_bonus is None:
             nome_completo = f"Arma Aleatória {bonus_display}"
        else:
             nome_completo = f"{nome_base} {bonus_display}"
             
        super().__init__(nome_completo, 'arma', mod)

class Armadura(Equipamento):
    def __init__(self):
        stat = random.choice(['HP', 'DEF']); val = gerar_modificador_aleatorio(stat)
        mod = {'ATK': 0, 'SPD': 0}
        if stat == 'HP': mod.update({'HP': val, 'DEF': 0})
        else: mod.update({'DEF': val, 'HP': 0})
        
        mod_str = []
        for stat, val in mod.items():
            if val > 0: mod_str.append(f"+{val} {stat}")
        nome_completo = f"Armadura Aleatória ({', '.join(mod_str)})"
        
        super().__init__(nome_completo, 'armadura', mod)

class Bota(Equipamento):
    def __init__(self):
        spd = gerar_modificador_aleatorio('SPD')
        mod = {'SPD': spd, 'ATK': 0, 'DEF': 0, 'HP': 0}
        
        mod_str = []
        for stat, val in mod.items():
            if val > 0: mod_str.append(f"+{val} {stat}")
        nome_completo = f"Botas Aleatórias ({', '.join(mod_str)})"
        
        super().__init__(nome_completo, 'bota', mod)

class Luva(Equipamento):
    def __init__(self):
        stat = random.choice(['HP', 'DEF']); val = gerar_modificador_aleatorio(stat)
        mod = {'ATK': 0, 'SPD': 0}
        if stat == 'HP': mod.update({'HP': val, 'DEF': 0})
        else: mod.update({'DEF': val, 'HP': 0})
        
        mod_str = []
        for stat, val in mod.items():
            if val > 0: mod_str.append(f"+{val} {stat}")
        nome_completo = f"Luvas Aleatórias ({', '.join(mod_str)})"
        
        super().__init__(nome_completo, 'luva', mod)

def gerar_equipamento_aleatorio():
    classes_equip = [Arma, Armadura, Bota, Luva]
    ClasseEquip = random.choice(classes_equip)
    return ClasseEquip()

ESPADA_CURTA = Arma(atk_bonus=1, nome_base="Espada Curta Inicial")
VARA_MOFADA = Arma(atk_bonus=1, nome_base="Vara Mofada Inicial")
ARCO_GALHOS = Arma(atk_bonus=1, nome_base="Arco de Galhos Inicial")

class StatusEffect:
    def __init__(self, nome, duracao_max):
        self.nome = nome
        self.duracao_max = duracao_max
        self.duracao_restante = duracao_max
        self.stacks = 1
        
    def aplicar(self, target, battle):
        if self.nome not in target.status_effects:
            target.status_effects[self.nome] = self
            battle.registrar(f" {target.nome} recebeu o status: {self.nome}.", 'info')
        else:
            target.status_effects[self.nome].stacks += 1
            target.status_effects[self.nome].duracao_restante = self.duracao_max
            battle.registrar(f" {target.nome} acumulou {self.nome} ({target.status_effects[self.nome].stacks}x) e a duração foi resetada.", 'info')

class Queimacao(StatusEffect):
    def __init__(self): super().__init__("Queimação", duracao_max=2)

def calcular_dano_rpg(atacante, defensor, dano_base_extra=0, defensor_ignora_def_bonus=False):
    bonus_atk = atacante.forca // 5; d_atk_roll = Dado.rolar(1, 6); d_atk_total = d_atk_roll + bonus_atk + dano_base_extra
    bonus_def = defensor.defesa // 6; d_def_roll = Dado.rolar(1, 6)
    
    if defensor_ignora_def_bonus: def_bonus_used = 0; d_def_total = d_def_roll
    else: def_bonus_used = bonus_def; d_def_total = d_def_roll + def_bonus_used
    
    is_crit_roll = (d_atk_roll == 6); is_crit_buff = (atacante.crit_chance_buff > 0); is_crit = is_crit_roll or is_crit_buff
    dano_bruto = d_atk_total - d_def_total
    if dano_bruto < 0: dano_final = 0 
    elif dano_bruto == 0: dano_final = 1 
    else: dano_final = dano_bruto
    if is_crit and dano_final > 0: dano_final *= 2
    log_roll = f" | Rolagens: ATK={d_atk_roll}+{bonus_atk}+{dano_base_extra}={d_atk_total} vs DEF={d_def_roll}+{def_bonus_used}={d_def_total} "
    
    return dano_final, log_roll, is_crit

class Personagem(ABC):
    def __init__(self, nome, vida_max, forca, defesa, velocidade, arma_inicial=None):
        self.nome = nome
        self._vida_max_base = vida_max
        self._forca_base = forca
        self._defesa_base = defesa
        self._velocidade_base = velocidade
        
        self.equipamento = {'arma': None, 'armadura': None, 'bota': None, 'luva': None}
        self.inventario = Inventario()
        self.status_effects = {} 
        self.crit_chance_buff = 0 
        self.arma_elemento_fogo_duracao = 0 
        
        if arma_inicial: self.equipar_item(arma_inicial, is_initial=True)
        
        self._vida = self.vida_max
        
        self.nivel = 1; self.xp_atual = 0; self.xp_proximo_nivel = 10; self.pontos_atributos_livres = 0; self.nivel_max = 20

    @property
    def forca(self):
        bonus = sum(e.modificadores.get('ATK', 0) for e in self.equipamento.values() if e)
        return self._forca_base + bonus

    @property
    def defesa(self):
        bonus = sum(e.modificadores.get('DEF', 0) for e in self.equipamento.values() if e)
        return self._defesa_base + bonus
        
    @property
    def velocidade(self):
        bonus = sum(e.modificadores.get('SPD', 0) for e in self.equipamento.values() if e)
        return self._velocidade_base + bonus
        
    @property
    def vida_max(self):
        bonus = sum(e.modificadores.get('HP', 0) for e in self.equipamento.values() if e)
        return self._vida_max_base + bonus

    @property
    def vida(self): return self._vida
    @vida.setter
    def vida(self, v): self._vida = max(0, min(v, self.vida_max))
    
    def equipar_item(self, item, battle=None, is_initial=False):
        if not isinstance(item, Equipamento): return False

        slot = item.slot
        old_item = self.equipamento[slot]
        
        if is_initial:
            self.equipamento[slot] = item
            return True

        if old_item:
            print(f" {self.nome} já tem {old_item.nome} equipado no slot {slot}.")
            print(f"Deseja trocar por {item.nome}? O item antigo será movido para o inventário. (S/N)")
            
            while True:
                choice = input("> ").upper()
                if choice == 'S': break
                elif choice == 'N':
                    if battle: battle.registrar(f" {old_item.nome} manteve {old_item.nome}. Não equipado.", 'info')
                    return False
                else: print("Escolha inválida.")
        
        hp_before = self.vida
        hp_max_before = self.vida_max 
        
        if old_item: 
            self.inventario.adicionar(old_item)
            if battle: battle.registrar(f" {old_item.nome} removido e movido para o inventário.", 'info')
        
        self.equipamento[slot] = item
        
        hp_max_after = self.vida_max
        hp_diff = hp_max_after - hp_max_before
        self.vida = hp_before + hp_diff 

        if battle: battle.registrar(f" {self.nome} equipou **{item.nome}** no slot {slot}!", 'equip')
        return True
    
    def receber_dano(self, dano_calculado): self.vida -= dano_calculado; return dano_calculado
    def curar(self, valor_cura): antes = self.vida; self.vida += valor_cura; return self.vida - antes
    def esta_vivo(self): return self.vida > 0
    def ganhar_xp(self, quantidade, battle):
        if self.nivel >= self.nivel_max: return
        antes = self.nivel
        self.xp_atual += quantidade
        battle.registrar(f" {self.nome} ganhou {quantidade} XP. ({self.xp_atual}/{self.xp_proximo_nivel})", 'xp')
        while self.xp_atual >= self.xp_proximo_nivel and self.nivel < self.nivel_max:
            self.upar_nivel(battle)
        return self.nivel > antes
    def upar_nivel(self, battle):
        self.nivel += 1
        self.xp_atual -= self.xp_proximo_nivel
        self.xp_proximo_nivel = self.nivel * 10 
        self.pontos_atributos_livres += 5
        battle.registrar(f" {self.nome} subiu para o **NÍVEL {self.nivel}**!", 'crit_hit')
        battle.registrar(f" {self.nome} recebeu **+5 Pontos** de Atributo Livres!", 'crit_hit')
    def adicionar_ponto_atributo(self, attr_name, quantidade):
        if attr_name == '_vida_max_base': self._vida_max_base += quantidade; self.vida += quantidade
        elif attr_name == '_forca_base': self._forca_base += quantidade
        elif attr_name == '_defesa_base': self._defesa_base += quantidade
        elif attr_name == '_velocidade_base': self._velocidade_base += quantidade
        self.pontos_atributos_livres -= quantidade
    def get_status(self):
        status_str = ", ".join(f"{s.nome} ({s.stacks}x, {s.duracao_restante}T)" for s in self.status_effects.values())
        if status_str: status_str = f"| Status: {status_str}"
        equip_info = " | Equip:"
        for slot, item in self.equipamento.items():
            equip_info += f" {slot[0].upper()}: {item.get_bonus_str() if item else '[Vazio]'}"
        return (f"[{self.nome} - NV:{self.nivel} ({self.xp_atual}/{self.xp_proximo_nivel}XP)] HP: {self.vida}/{self.vida_max} | ATK: {self.forca} | DEF: {self.defesa} | SPD: {self.velocidade} {equip_info} {status_str}")
    
    def distribuir_xp_party(self, monstro, battle, party):
        xp_total = 5; xp_bonus = 3
        for heroi in party:
            if heroi.esta_vivo():
                xp_ganha = xp_total
                if heroi is self: xp_ganha += xp_bonus
                heroi.ganhar_xp(xp_ganha, battle)
        battle.registrar(f" PARTY GAIN: {xp_total} XP base, {self.nome} (+{xp_bonus} bônus) pela vitória!", 'xp')
        
        item_drop = gerar_equipamento_aleatorio()
        self.inventario.adicionar(item_drop)
        battle.registrar(f" DROP: {monstro.nome} deixou cair **{item_drop.nome}**! Foi para o inventário de {self.nome}.", 'item')
    
    @abstractmethod
    def atacar(self, alvo, battle, party): pass

class Guerreiro(Personagem):
    def __init__(self, nome, stats): super().__init__(nome, stats["HP"], stats["ATK"], stats["DEF"], stats["SPD"], arma_inicial=ESPADA_CURTA)
    
    def atacar(self, alvo, battle, party):
        if not self.esta_vivo() or not alvo.esta_vivo(): return 0
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(self, alvo)
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0: battle.registrar(f"{crit_str} [GUERREIRO] {self.nome} ataca {alvo.nome} ({log_roll}) causando {causado}!", 'damage')
        else: battle.registrar(f" [MISS] {self.nome} erra o golpe em {alvo.nome} ({log_roll}).", 'miss')
        
        if not alvo.esta_vivo() and isinstance(alvo, Monstro):
            self.distribuir_xp_party(alvo, battle, party)
        return causado
    
    def get_habilidades_ativas(self): return {"classe": "Chamado do Líder", "arma": "Coronhada"}
    class ChamadoLiderBuff(StatusEffect): 
         def __init__(self, atk, def_val): super().__init__("Chamado do Líder", 2); self.atk = atk; self.def_val = def_val
    def usar_habilidade_classe(self, alvo, party, battle): 
        if alvo not in party or not alvo.esta_vivo(): battle.registrar(f" Alvo inválido para Chamado do Líder.", 'error'); return 0
        buff_atk = Dado.rolar(1, 12); buff_def = Dado.rolar(1, 12)
        alvo._forca_base += buff_atk; alvo._defesa_base += buff_def
        self.ChamadoLiderBuff(buff_atk, buff_def).aplicar(alvo, battle)
        battle.registrar(f" [CHAMADO] {self.nome} bufou {alvo.nome}: +{buff_atk} ATK, +{buff_def} DEF por 2T!", 'skill'); return 1
    def coronhada(self, alvo, party, battle):
        if not alvo.esta_vivo(): return 0
        dano_extra = 2 
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(self, alvo, dano_base_extra=dano_extra)
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0: battle.registrar(f"{crit_str} [CORONHADA] {self.nome} usa Coronhada em {alvo.nome} ({log_roll}) causando {causado}!", 'damage')
        else: battle.registrar(f" [MISS] {self.nome} erra Coronhada em {alvo.nome} ({log_roll}).", 'miss')
        if not alvo.esta_vivo() and isinstance(alvo, Monstro): self.distribuir_xp_party(alvo, battle, party)
        return causado

class Mago(Personagem): 
    def __init__(self, nome, stats): super().__init__(nome, stats["HP"], stats["ATK"], stats["DEF"], stats["SPD"], arma_inicial=VARA_MOFADA)
        
    def atacar(self, alvo, battle, party):
        if not self.esta_vivo() or not alvo.esta_vivo(): return 0
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(self, alvo, defensor_ignora_def_bonus=True)
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0: battle.registrar(f"{crit_str} [MAGO] {self.nome} lança magia em {alvo.nome} ({log_roll}) causando {causado}!", 'skill')
        else: battle.registrar(f" [MISS] {self.nome} erra a magia em {alvo.nome} ({log_roll}).", 'miss')
        
        if not alvo.esta_vivo() and isinstance(alvo, Monstro):
            self.distribuir_xp_party(alvo, battle, party)
        return causado

    def get_habilidades_ativas(self): return {"classe": "Bola de Fogo", "arma": "Ignis"}
    def usar_habilidade_classe(self, alvo, party, battle):
        if not alvo.esta_vivo(): return 0
        dano_extra = 1 
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(self, alvo, dano_base_extra=dano_extra, defensor_ignora_def_bonus=True)
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0:
            battle.registrar(f"{crit_str} [BOLA FOGO] {self.nome} lança Bola de Fogo em {alvo.nome} ({log_roll}) causando {causado}!", 'skill')
            if Dado.rolar(1, 100) <= 30: Queimacao().aplicar(alvo, battle)
        else: battle.registrar(f" [MISS] {self.nome} erra a Bola de Fogo em {alvo.nome} ({log_roll}).", 'miss')
        if not alvo.esta_vivo() and isinstance(alvo, Monstro): self.distribuir_xp_party(alvo, battle, party)
        return causado
    def usar_habilidade_arma(self, alvo, party, battle):
        if alvo not in party or not alvo.equipamento['arma'] or not alvo.esta_vivo(): battle.registrar(f" Alvo inválido ou sem arma para Ignis.", 'error'); return 0
        alvo.arma_elemento_fogo_duracao = 2 
        battle.registrar(f" [IGNIS] {self.nome} imbuiu a arma de {alvo.nome} com Fogo por 2 turnos!", 'skill'); return 1

class Arqueiro(Personagem): 
    def __init__(self, nome, stats): 
        super().__init__(nome, stats["HP"], stats["ATK"], stats["DEF"], stats["SPD"], arma_inicial=ARCO_GALHOS)
        self.dano_passivo_extra = 1

    def atacar(self, alvo, battle, party):
        if not self.esta_vivo() or not alvo.esta_vivo(): return 0
        dano_extra = self.dano_passivo_extra 
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(self, alvo, dano_base_extra=dano_extra)
        is_double_shot = Dado.rolar(1, 10) <= 3 
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        
        if causado > 0: battle.registrar(f"{crit_str} [ARQUEIRO] {self.nome} atira em {alvo.nome} ({log_roll}) causando {causado}!", 'damage')
        else: battle.registrar(f" [MISS] {self.nome} erra o tiro em {alvo.nome} ({log_roll}).", 'miss')
            
        dano_total = causado
        
        if is_double_shot and alvo.esta_vivo():
            battle.registrar(f" [COMBO] {self.nome} dispara um segundo tiro!", 'crit_hit')
            dano_total += self.atacar(alvo, battle, party) 
        
        if not alvo.esta_vivo() and isinstance(alvo, Monstro):
            self.distribuir_xp_party(alvo, battle, party)

        return dano_total
    
    def get_habilidades_ativas(self): return {"classe": "Olho de Águia", "arma": "Nenhuma (Passiva)"}
    class OlhoAguiaBuff(StatusEffect): 
         def __init__(self): super().__init__("Olho de Águia (100% CRIT)", 2)
    def usar_habilidade_classe(self, alvo, party, battle):
        if alvo not in party or not alvo.esta_vivo(): battle.registrar(f" Alvo inválido para Olho de Águia.", 'error'); return 0
        alvo.crit_chance_buff = 2 
        self.OlhoAguiaBuff().aplicar(alvo, battle)
        battle.registrar(f" [OLHO ÁGUIA] {self.nome} bufou {alvo.nome}: 100% de chance de CRÍTICO por 2 rodadas!", 'skill'); return 1

def gerar_status_soma_25_4_stats():
    soma = 25
    cuts = sorted(random.sample(range(1, soma), 3))
    s1 = cuts[0]; s2 = cuts[1] - cuts[0]; s3 = cuts[2] - cuts[1]; s4 = soma - cuts[2]
    stats = [s1, s2, s3, s4] 
    random.shuffle(stats)
    return {"vida_max": stats[0] + 10, "forca": stats[1] + 5, "defesa": stats[2] + 5, "velocidade": stats[3] + 5}

class Monstro(Personagem):
    def __init__(self, nome, forca_extra=0):
        stats = gerar_status_soma_25_4_stats()
        super().__init__(nome, stats["vida_max"], stats["forca"] + forca_extra, stats["defesa"], stats["velocidade"])
        self._forca_base += forca_extra 
        
    def atacar(self, alvo, battle, party):
        if not self.esta_vivo() or not alvo.esta_vivo(): return 0
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(self, alvo)
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0: battle.registrar(f"{crit_str} [INIMIGO] {self.nome} ataca {alvo.nome} ({log_roll}) causando {causado}!", 'damage')
        else: battle.registrar(f" [MISS] {self.nome} erra o ataque em {alvo.nome} ({log_roll}).", 'miss')
        if not alvo.esta_vivo(): battle.registrar(f" {alvo.nome} foi derrotado por {self.nome}!", 'damage')
        return causado
    
    def usar_habilidade_classe(self, alvo, party, battle): return 0
    def get_habilidades_ativas(self): return {"classe": "Nenhuma", "arma": "Nenhuma"}
    
class Orc(Monstro): 
    def __init__(self, i): super().__init__(f"Orc Brutal #{i}")

class Ogro(Monstro): 
    def __init__(self, i): super().__init__(f"Ogro Pesado #{i}", forca_extra=5) 
        
class Bruxa(Monstro):
    def __init__(self, i): super().__init__(f"Bruxa Sombria #{i}") 
        
    def atacar(self, alvo, battle, party):
        if Dado.rolar(1, 10) == 10:
             dano_magico = self.forca + Dado.rolar(5, 15) 
             causado = alvo.receber_dano(dano_magico)
             battle.registrar(f" [MAGIA] {self.nome} lança Maldição Poderosa em {alvo.nome} causando {causado}!", 'skill')
             if not alvo.esta_vivo(): battle.registrar(f" {alvo.nome} foi derrotado por {self.nome}!", 'damage')
             return causado
        return super().atacar(alvo, battle, party)


def gerar_monstro_aleatorio_escalado(andar, is_extra=False):
    monster_types = [Orc, Ogro, Bruxa]
    MonstroClasse = random.choice(monster_types)
    fator_escala = 1.1 ** (andar - 1) 
    monstro = MonstroClasse(andar)
    monstro._vida_max_base = math.ceil(monstro._vida_max_base * fator_escala)
    monstro._vida = monstro.vida_max
    monstro._forca_base = math.ceil(monstro._forca_base * fator_escala)
    monstro._defesa_base = math.ceil(monstro._defesa_base * fator_escala)
    monstro._velocidade_base = math.ceil(monstro._velocidade_base * fator_escala)
    tipo_andar = "Principal"
    if is_extra: tipo_andar = "Adicional"
    monstro.nome = f"Andar {andar} ({tipo_andar}) | {monstro.nome}"
    return monstro


class Batalha:
    def __init__(self, herois, inimigos):
        self.herois=herois; self.inimigos=inimigos
        self.ordem = herois + inimigos
        self.log = []
        self.turno_idx = 0
        self.turno_ativo = None 
        self.ordem.sort(key=lambda u: (u.velocidade, u.forca), reverse=True)
        self.registrar(f"Iniciativa: {[u.nome for u in self.ordem]}", 'info')
        self.rodada = 1

    def registrar(self, t, tag='default'): self.log.append(t)
    def unidades_vivas(self,grupo): return [u for u in grupo if u.esta_vivo()]
    def acaba(self):
        herois_vivos = any(u.esta_vivo() for u in self.herois)
        inimigos_vivos = any(u.esta_vivo() for u in self.inimigos)
        return not (herois_vivos and inimigos_vivos)

    def aplicar_status_turn_start(self, unit):
        if "Queimacao" in unit.status_effects:
            q = unit.status_effects["Queimacao"]
            dano_queimacao = q.stacks * 1 
            unit.vida -= dano_queimacao
            self.registrar(f" {unit.nome} sofre {dano_queimacao} de dano por Queimação ({q.stacks} acúmulos).", 'fire')
            if not unit.esta_vivo(): self.registrar(f" {unit.nome} morreu devido a Queimação.", 'damage'); return False
        return True 

    def gerenciar_status_pos_turno(self, unit):
        if not unit.esta_vivo(): return
        if unit.crit_chance_buff > 0: unit.crit_chance_buff -= 1
        if unit.arma_elemento_fogo_duracao > 0: unit.arma_elemento_fogo_duracao -= 1

        if "Chamado do Líder" in unit.status_effects:
            status = unit.status_effects["Chamado do Líder"]
            status.duracao_restante -= 1
            if status.duracao_restante <= 0:
                 unit._forca_base -= status.atk; unit._defesa_base -= status.def_val
                 self.registrar(f" Chamado do Líder em {unit.nome} terminou e reverteu o buff.", 'info')
                 del unit.status_effects["Chamado do Líder"]
        if "Queimacao" in unit.status_effects:
            q = unit.status_effects["Queimacao"]
            q.duracao_restante -= 1
            if q.duracao_restante <= 0:
                 self.registrar(f" Efeito Queimação em {unit.nome} terminou.", 'info')
                 del unit.status_effects["Queimacao"]

    def proximo_turno(self):
        if self.acaba(): return

        while True:
            self.turno_ativo = self.ordem[self.turno_idx % len(self.ordem)]
            self.turno_idx += 1
            
            if self.turno_ativo.esta_vivo(): break
            
            if self.turno_idx >= len(self.ordem):
                 self.rodada += 1
                 self.ordem = self.unidades_vivas(self.herois) + self.unidades_vivas(self.inimigos)
                 self.ordem.sort(key=lambda u: (u.velocidade, u.forca), reverse=True)
                 self.turno_idx = 0
                 self.registrar("--- Nova Rodada Iniciada ---", 'turn_start')
                 if not self.ordem: return
                 self.turno_ativo = self.ordem[self.turno_idx % len(self.ordem)]
                 self.turno_idx += 1
        
        if not self.aplicar_status_turn_start(self.turno_ativo): return self.proximo_turno()
            
        print(f"\n--- Turno Ativo: {self.turno_ativo.nome} (SPD: {self.turno_ativo.velocidade}, ATK: {self.turno_ativo.forca}) ---")
        
        if self.turno_ativo in self.herois: 
            return "Jogador"
        else:
            self.ai_turn(self.turno_ativo)
            self.gerenciar_status_pos_turno(self.turno_ativo)
            if any(h.esta_vivo() for h in self.herois):
                input("Pressione Enter para o próximo turno (Inimigo atacou)...")
            return self.proximo_turno()

    def ai_turn(self, unit):
        vivos = self.unidades_vivas(self.herois)
        if not vivos: return
        alvo = random.choice(vivos) 
        unit.atacar(alvo, self, self.herois)
        
    def exibir_log(self):
        print("\n" + "="*30 + " LOG DE COMBATE " + "="*30)
        for t in self.log: print(t)
        print("="*76 + "\n")
        self.log = [] 

def distribuir_pontos_livres(heroi, battle):
    limpar_console()
    battle.registrar(f" **ATENÇÃO!** {heroi.nome} tem {heroi.pontos_atributos_livres} Pontos de Atributo Livres!", 'crit_hit')
    print("=======================================")
    print(f"DISTRIBUIÇÃO DE PONTOS: {heroi.nome}")
    print("=======================================")
    
    while heroi.pontos_atributos_livres > 0:
        print(f"\n[PONTOS LIVRES: {heroi.pontos_atributos_livres}]")
        print(f"Stats Base: HP={heroi._vida_max_base} | ATK={heroi._forca_base} | DEF={heroi._defesa_base} | SPD={heroi._velocidade_base}")
        print(f"Stats Efetivos: HP={heroi.vida_max} | ATK={heroi.forca} | DEF={heroi.defesa} | SPD={heroi.velocidade}")
        print("Atributos (Base): [H]P Max | [A]TK | [D]EF | [S]PD")
        
        escolha = input("Adicionar pontos a (H/A/D/S) ou (FIM) para terminar: ").upper()
        if escolha == "FIM": break
        
        atributo_map = {'H': '_vida_max_base', 'A': '_forca_base', 'D': '_defesa_base', 'S': '_velocidade_base'}
        if escolha not in atributo_map: print("Escolha inválida."); continue
            
        attr_name = atributo_map[escolha]
        
        try:
            quantidade = int(input(f"Quantos pontos adicionar a {escolha} ({attr_name.replace('_', ' ')} base)? "))
            if quantidade <= 0 or quantidade > heroi.pontos_atributos_livres: print(f"Quantidade inválida. Máximo: {heroi.pontos_atributos_livres}"); continue
            
            heroi.adicionar_ponto_atributo(attr_name, quantidade)
            battle.registrar(f" {heroi.nome} adicionou {quantidade} em {attr_name.replace('_', ' ')}.", 'info')
        except ValueError: print("Entrada inválida. Digite um número.")
    
    print(f"\nDistribuição finalizada para {heroi.nome}.")
    input("Pressione Enter para retornar ao combate...")
    limpar_console()

def menu_gerenciar_inventario(heroi):
    limpar_console()
    print("=======================================")
    print(f"GERENCIAR INVENTÁRIO: {heroi.nome}")
    print("=======================================")
    
    while True:
        print(f"\nStatus de {heroi.nome}: HP:{heroi.vida}/{heroi.vida_max} | ATK:{heroi.forca} | DEF:{heroi.defesa} | SPD:{heroi.velocidade}")
        print("\n--- EQUIPAMENTO ---")
        for slot, item in heroi.equipamento.items():
            print(f"[{slot.upper()[0]}] {slot.capitalize()}: {item.nome if item else '[Vazio]'}")
            
        print("\n--- INVENTÁRIO (Equipamentos) ---")
        itens_equip = [item for item in heroi.inventario.itens if isinstance(item, Equipamento)]
        
        if not itens_equip:
            print("Inventário de Equipamentos vazio.")
            print("[FIM] para retornar.")
            escolha = input("> ").upper()
            if escolha == 'FIM': break
            continue

        for i, item in enumerate(itens_equip):
            print(f"[{i+1}] {item.nome} (Slot: {item.slot.capitalize()})")
        
        print(f"\n[1-{len(itens_equip)}] Para equipar item | [FIM] Para retornar.")
        escolha = input("> ").upper()
        
        if escolha == 'FIM': break
        
        try:
            idx = int(escolha) - 1
            if 0 <= idx < len(itens_equip):
                item_selecionado = itens_equip[idx]
                
                if heroi.equipar_item(item_selecionado):
                    heroi.inventario.remover(item_selecionado)
                    print(f" {item_selecionado.nome} equipado.")
                
            else: print("Escolha inválida.")
        except ValueError: print("Entrada inválida.")
        input("Pressione Enter para continuar...")
        limpar_console()
        

def criar_personagem_e_party():
    limpar_console()
    print("---------------------------------------")
    print(" CRIAÇÃO DE PERSONAGEM E PARTY ")
    print("---------------------------------------")
    CLASSES = {'G': Guerreiro, 'M': Mago, 'A': Arqueiro}
    print("Escolha sua Classe principal (receberá 15 pontos adicionais):")
    for k, C in CLASSES.items(): print(f"[{k}] {C.__name__}")
    
    while True:
        escolha = input("Sua escolha (G/M/A): ").upper()
        if escolha in CLASSES: ClassePrincipal = CLASSES[escolha]; break
        print("Escolha inválida.")
        
    nome = input(f"Digite o nome do seu {ClassePrincipal.__name__}: ")
    stats_base_principal = gerar_status_base_aleatorio()
    pontos_disponiveis = 15
    stats = stats_base_principal.copy()
    
    print(f"\nStatus Base (Aleatório): HP={stats['HP']}, ATK={stats['ATK']}, DEF={stats['DEF']}, SPD={stats['SPD']}")
    print(f"Você tem {pontos_disponiveis} pontos para distribuir (15 pontos).")

    while pontos_disponiveis > 0:
        print(f"\n[PONTOS: {pontos_disponiveis}] Status Atuais: HP={stats['HP']}, ATK={stats['ATK']}, DEF={stats['DEF']}, SPD={stats['SPD']}")
        escolha = input("Adicionar pontos a (HP/ATK/DEF/SPD) ou (FIM) para terminar: ").upper()
        if escolha == "FIM": break
        if escolha not in stats: print("Escolha inválida. Use HP, ATK, DEF, ou SPD."); continue
            
        try:
            quantidade = int(input(f"Quantos pontos adicionar a {escolha}? "))
            if quantidade <= 0 or quantidade > pontos_disponiveis: print(f"Quantidade inválida. Máximo: {pontos_disponiveis}"); continue
            stats[escolha] += quantidade; pontos_disponiveis -= quantidade
        except ValueError: print("Entrada inválida. Digite um número.")

    heroi_principal = ClassePrincipal(nome, stats)
    party = [heroi_principal]
    classes_restantes = [c for k, c in CLASSES.items() if c != ClassePrincipal]
    
    for C in classes_restantes:
        stats_aliado = gerar_status_base_aleatorio()
        
        party.append(C(f"Aliado ({C.__name__})", stats_aliado))

    for h in party:
        h.inventario.adicionar(PocaoCura())
        h.inventario.adicionar(PocaoCura())

    print("\n---------------------------------------")
    print("Party Criada:")
    for h in party: print(f"- {h.nome} ({h.__class__.__name__}) | NV: {h.nivel} | SPD: {h.velocidade} | Poções: {h.inventario.contar(PocaoCura)}")
    print("---------------------------------------")
    return party

def exibir_status(party, inimigo_atual, andar):
    print("\n" + "="*20 + f" STATUS DE COMBATE (ANDAR {andar}) " + "="*20)
    print("--- SUA PARTY (VIVOS) ---")
    herois_vivos = [h for h in party if h.esta_vivo()]
    for i, h in enumerate(herois_vivos): print(f"[{i+1}] {h.get_status()}")
    if not herois_vivos: print("Sua Party foi nocauteada!")
    
    print("\n--- INIMIGO ATUAL ---")
    if inimigo_atual.esta_vivo(): print(f"[0] {inimigo_atual.get_status()}")
    else: print(f"[0] {inimigo_atual.nome} derrotado!")
    print("="*75)

def loop_jogo():
    global Monstro, Orc, Ogro, Bruxa 
    
    party = criar_personagem_e_party()
    input("\nPressione Enter para começar a aventura contra os monstros!")
    
    for andar in range(1, 11):
        limpar_console()
        print(f"--- FASE DE PREPARAÇÃO: ANDAR {andar} ---")
        
        temp_battle = Batalha(party, [])
        for h in party:
            if h.esta_vivo() and h.pontos_atributos_livres > 0:
                distribuir_pontos_livres(h, temp_battle)
        
        herois_com_item_novo = []
        for h in party:
            itens_equip_inventario = [i for i in h.inventario.itens if isinstance(i, Equipamento)]
            if itens_equip_inventario:
                herois_com_item_novo.append(h)
        
        if herois_com_item_novo:
            print("\n **NOVIDADES NO INVENTÁRIO!**")
            for h in herois_com_item_novo:
                 itens_equip_inventario = [i for i in h.inventario.itens if isinstance(i, Equipamento)]
                 print(f" **{h.nome}** tem {len(itens_equip_inventario)} itens equipáveis novos e {h.inventario.contar(PocaoCura)} poções.")
            
            escolha = input("\nDeseja gerenciar inventário (equipar/trocar itens) para algum herói? (S/N): ").upper()
            
            if escolha == 'S':
                 for h in herois_com_item_novo:
                      print(f"\n--- Gerenciando {h.nome} ---")
                      menu_gerenciar_inventario(h)


        if not any(h.esta_vivo() for h in party): break

        inimigos_do_andar = [gerar_monstro_aleatorio_escalado(andar, is_extra=False)]
        
        while inimigos_do_andar:
            if not any(h.esta_vivo() for h in party): break
                
            inimigo_ativo = inimigos_do_andar.pop(0)

            limpar_console()
            print(f"=======================================")
            print(f"*** ANDAR {andar}: COMBATE CONTRA {inimigo_ativo.nome} ***")
            print("=======================================")
            if "Principal" in inimigo_ativo.nome: input("Pressione Enter para iniciar o duelo...")
            
            battle = Batalha(party, [inimigo_ativo])
            battle.proximo_turno()
            
            while not battle.acaba():
                limpar_console()
                battle.exibir_log()
                exibir_status(party, inimigo_ativo, andar)
                
                if battle.turno_ativo in party:
                    heroi_ativo = battle.turno_ativo
                    
                    print(f"\nTurno de **{heroi_ativo.nome}**.")
                    pocao_count = heroi_ativo.inventario.contar(PocaoCura)
                    print(f"[A]tacar | [H] Habilidade | [R] Curar (Poções: {pocao_count}x) | **[I]nspecionar/Status** | [P]assar Turno | [S]air")
                    acao = input("> ").upper()
                    
                    if acao == 'S': print("A party foge da batalha. Fim de jogo."); return
                    
                    elif acao == 'I':
                        exibir_status(party, inimigo_ativo, andar)
                        print(f"\nRetornando ao turno de **{heroi_ativo.nome}**.")
                        input("Pressione Enter para continuar...")
                        continue
                        

                    if acao == 'R':
                        if heroi_ativo.inventario.contar(PocaoCura) > 0:
                            pocao = next(item for item in heroi_ativo.inventario.itens if isinstance(item, PocaoCura))
                            pocao.usar(heroi_ativo, battle)
                            heroi_ativo.inventario.remover(pocao)
                            battle.gerenciar_status_pos_turno(heroi_ativo)
                            battle.proximo_turno()
                        else: print("Sem poções de cura disponíveis para este herói."); input("Pressione Enter para continuar...")

                    elif acao == 'A':
                        if inimigo_ativo.esta_vivo(): heroi_ativo.atacar(inimigo_ativo, battle, party)
                        battle.gerenciar_status_pos_turno(heroi_ativo)
                        battle.proximo_turno() 
                    
                    elif acao == 'H':
                        h = heroi_ativo.get_habilidades_ativas()
                        print(f"\nEscolha a habilidade:"); 
                        print(f"[C] Classe: {h['classe']}"); 
                        if h['arma'] != "Nenhuma (Passiva)": print(f"[W] Arma: {h['arma']}")
                        h_choice = input("> ").upper()

                        if h_choice == 'C' and h['classe'] == "Chamado do Líder":
                            herois_vivos = battle.unidades_vivas(party)
                            print("Escolha um aliado para o buff (1-3):")
                            for j, h_ally in enumerate(herois_vivos): print(f"[{j+1}] {h_ally.nome}")
                            try:
                                ally_idx = int(input("> ")); target = herois_vivos[ally_idx - 1]
                                heroi_ativo.usar_habilidade_classe(target, party, battle)
                                battle.gerenciar_status_pos_turno(heroi_ativo); battle.proximo_turno()
                            except Exception: print("Alvo inválido."); input("Pressione Enter para continuar..."); continue
                            
                        elif h_choice == 'C':
                            target = inimigo_ativo if h['classe'] in ["Bola de Fogo"] else heroi_ativo
                            heroi_ativo.usar_habilidade_classe(target, party, battle) 
                            battle.gerenciar_status_pos_turno(heroi_ativo); battle.proximo_turno()

                        elif h_choice == 'W' and h['arma'] == "Coronhada":
                            if inimigo_ativo.esta_vivo(): heroi_ativo.coronhada(inimigo_ativo, party, battle); battle.gerenciar_status_pos_turno(heroi_ativo); battle.proximo_turno()
                            else: print("Inimigo já derrotado."); input("Pressione Enter para continuar...")
                                
                        elif h_choice == 'W' and h['arma'] == "Ignis":
                            herois_vivos = battle.unidades_vivas(party)
                            print("Escolha um aliado para imbuir a arma (1-3):")
                            for j, h_ally in enumerate(herois_vivos): print(f"[{j+1}] {h_ally.nome}")
                            try:
                                ally_idx = int(input("> ")); target = herois_vivos[ally_idx - 1]
                                heroi_ativo.usar_habilidade_arma(target, party, battle)
                                battle.gerenciar_status_pos_turno(heroi_ativo); battle.proximo_turno()
                            except Exception: print("Alvo inválido."); input("Pressione Enter para continuar..."); continue
                            
                        else: print("Escolha de habilidade inválida."); input("Pressione Enter para continuar...")
                            
                    elif acao == 'P':
                        battle.registrar(f"{heroi_ativo.nome} passa o turno.", 'info')
                        battle.gerenciar_status_pos_turno(heroi_ativo)
                        battle.proximo_turno()
                    else: print("Ação inválida. Tente novamente."); input("Pressione Enter para continuar...")
                
            if any(h.esta_vivo() for h in party):
                limpar_console(); battle.exibir_log()
                print(f" **{inimigo_ativo.nome} foi derrotado!**")
                
                for h in party:
                    if h.esta_vivo():
                        curado = h.curar(h.vida_max // 4)
                        if curado > 0: print(f" {h.nome} (Party) recupera {curado} HP. HP Atual: {h.vida}/{h.vida_max}")
                
                for h in party:
                    if h.esta_vivo() and h.pontos_atributos_livres > 0:
                        distribuir_pontos_livres(h, battle)
                
                herois_com_item_novo = []
                for h in party:
                    itens_equip_inventario = [i for i in h.inventario.itens if isinstance(i, Equipamento)]
                    if itens_equip_inventario:
                        herois_com_item_novo.append(h)
                
                if herois_com_item_novo:
                    print("\n **NOVOS DROPS!**")
                    for h in herois_com_item_novo:
                         itens_equip_inventario = [i for i in h.inventario.itens if isinstance(i, Equipamento)]
                         print(f" **{h.nome}** tem {len(itens_equip_inventario)} itens equipáveis novos e {h.inventario.contar(PocaoCura)} poções.")
                    
                    escolha = input("\nDeseja gerenciar inventário (equipar/trocar itens) para algum herói? (S/N): ").upper()
                    
                    if escolha == 'S':
                         for h in herois_com_item_novo:
                              print(f"\n--- Gerenciando {h.nome} ---")
                              menu_gerenciar_inventario(h)


                if andar < 10 and random.random() < 0.45:
                    monstro_extra = gerar_monstro_aleatorio_escalado(andar, is_extra=True)
                    inimigos_do_andar.append(monstro_extra)
                    print(f" Um novo inimigo apareceu! Chance de 45% acionada. Prepare-se para: {monstro_extra.nome}!")
                elif not inimigos_do_andar:
                    input("Pressione Enter para seguir para o próximo andar...")

            else:
                limpar_console(); battle.exibir_log()
                print(f" Sua Party foi derrotada por {inimigo_ativo.nome} no ANDAR {andar}. Fim de Jogo!")
                return
        
    if any(h.esta_vivo() for h in party):
        limpar_console(); print("\n======================================="); print(" PARABÉNS! VOCÊ DERROTOU TODOS OS MONSTROS DOS 10 ANDARES! "); print("=======================================")

if __name__ == "__main__":
    try:
        loop_jogo()
    except Exception as e:
        print(f"Ocorreu um erro fatal: {e}")
        sys.exit(1)