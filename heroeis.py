from __future__ import annotations

from abc import ABC, abstractmethod
import math
import random
import sys
from typing import Dict, List, Optional, Tuple

try:
    import tkinter as tk
    from tkinter import messagebox
except Exception:  # pragma: no cover - fallback para ambientes sem Tk
    print("Este jogo requer Tkinter para ser executado.")
    sys.exit(1)


class Dado:
    @staticmethod
    def rolar(a: int = 1, b: int = 6) -> int:
        return random.randint(a, b)


def gerar_status_base_aleatorio() -> Dict[str, int]:
    return {
        "HP": Dado.rolar(8, 15),
        "ATK": Dado.rolar(8, 15),
        "DEF": Dado.rolar(8, 15),
        "SPD": Dado.rolar(8, 15),
    }


def distribuir_pontos_aleatorio(stats: Dict[str, int], pontos: int) -> Dict[str, int]:
    atualizado = stats.copy()
    atributos = list(atualizado.keys())
    for _ in range(pontos):
        atributo = random.choice(atributos)
        atualizado[atributo] += 1
    return atualizado


def gerar_modificador_aleatorio(tipo: str) -> int:
    if tipo == "ATK":
        return Dado.rolar(1, 10)
    if tipo in ("HP", "DEF"):
        return Dado.rolar(1, 10)
    if tipo == "SPD":
        return Dado.rolar(1, 15)
    return 0


class Item:
    def __init__(self, nome: str) -> None:
        self.nome = nome


class PocaoCura(Item):
    def __init__(self) -> None:
        super().__init__("Poção de Cura")

    def usar(self, heroi: "Personagem", battle: "Batalha") -> int:
        cura = Dado.rolar(1, 12)
        curado = heroi.curar(cura)
        battle.registrar(
            f" {heroi.nome} usou {self.nome} e recuperou {curado} HP. ({heroi.vida}/{heroi.vida_max})",
            "heal",
        )
        return curado


class Inventario:
    def __init__(self) -> None:
        self.itens: List[Item] = []

    def adicionar(self, item: Item) -> None:
        self.itens.append(item)

    def remover(self, item: Item) -> bool:
        self.itens.remove(item)
        return True

    def contar(self, item_class: type) -> int:
        return sum(1 for item in self.itens if isinstance(item, item_class))

    def listar(self) -> List[Item]:
        return list(self.itens)


class Equipamento(Item):
    def __init__(self, nome: str, slot: str, modificadores: Dict[str, int]) -> None:
        super().__init__(nome)
        self.slot = slot
        self.modificadores = modificadores

    def get_bonus_str(self) -> str:
        mod_str = [f"+{val} {stat}" for stat, val in self.modificadores.items() if val > 0]
        return f"({', '.join(mod_str)})" if mod_str else "(Sem bônus)"


class Arma(Equipamento):
    def __init__(self, atk_bonus: Optional[int] = None, nome_base: str = "Arma") -> None:
        atk = atk_bonus if atk_bonus is not None else gerar_modificador_aleatorio("ATK")
        mod = {"ATK": atk, "DEF": 0, "HP": 0, "SPD": 0}
        mod_str = [f"+{val} {stat}" for stat, val in mod.items() if val > 0]
        bonus_display = f"({', '.join(mod_str)})" if mod_str else "(Sem bônus)"
        if atk_bonus is None:
            nome_completo = f"Arma Aleatória {bonus_display}"
        else:
            nome_completo = f"{nome_base} {bonus_display}"
        super().__init__(nome_completo, "arma", mod)


class Armadura(Equipamento):
    def __init__(self) -> None:
        stat = random.choice(["HP", "DEF"])
        val = gerar_modificador_aleatorio(stat)
        mod = {"ATK": 0, "DEF": 0, "HP": 0, "SPD": 0}
        mod[stat] = val
        mod_str = [f"+{value} {key}" for key, value in mod.items() if value > 0]
        nome_completo = f"Armadura Aleatória ({', '.join(mod_str)})" if mod_str else "Armadura Aleatória"
        super().__init__(nome_completo, "armadura", mod)


class Bota(Equipamento):
    def __init__(self) -> None:
        spd = gerar_modificador_aleatorio("SPD")
        mod = {"ATK": 0, "DEF": 0, "HP": 0, "SPD": spd}
        mod_str = [f"+{value} {key}" for key, value in mod.items() if value > 0]
        nome_completo = f"Botas Aleatórias ({', '.join(mod_str)})" if mod_str else "Botas Aleatórias"
        super().__init__(nome_completo, "bota", mod)


class Luva(Equipamento):
    def __init__(self) -> None:
        stat = random.choice(["HP", "DEF"])
        val = gerar_modificador_aleatorio(stat)
        mod = {"ATK": 0, "DEF": 0, "HP": 0, "SPD": 0}
        mod[stat] = val
        mod_str = [f"+{value} {key}" for key, value in mod.items() if value > 0]
        nome_completo = f"Luvas Aleatórias ({', '.join(mod_str)})" if mod_str else "Luvas Aleatórias"
        super().__init__(nome_completo, "luva", mod)


def gerar_equipamento_aleatorio() -> Equipamento:
    classes_equip = [Arma, Armadura, Bota, Luva]
    equip_class = random.choice(classes_equip)
    return equip_class()


ESPADA_CURTA = Arma(atk_bonus=1, nome_base="Espada Curta Inicial")
VARA_MOFADA = Arma(atk_bonus=1, nome_base="Vara Mofada Inicial")
ARCO_GALHOS = Arma(atk_bonus=1, nome_base="Arco de Galhos Inicial")


class StatusEffect:
    def __init__(self, nome: str, duracao_max: int) -> None:
        self.nome = nome
        self.duracao_max = duracao_max
        self.duracao_restante = duracao_max
        self.stacks = 1

    def aplicar(self, target: "Personagem", battle: "Batalha") -> None:
        if self.nome not in target.status_effects:
            target.status_effects[self.nome] = self
            battle.registrar(f" {target.nome} recebeu o status: {self.nome}.", "info")
        else:
            status = target.status_effects[self.nome]
            status.stacks += 1
            status.duracao_restante = self.duracao_max
            battle.registrar(
                f" {target.nome} acumulou {self.nome} ({status.stacks}x) e a duração foi resetada.",
                "info",
            )


class Queimacao(StatusEffect):
    def __init__(self) -> None:
        super().__init__("Queimação", duracao_max=2)


def calcular_dano_rpg(
    atacante: "Personagem",
    defensor: "Personagem",
    dano_base_extra: int = 0,
    defensor_ignora_def_bonus: bool = False,
) -> Tuple[int, str, bool]:
    bonus_atk = atacante.forca // 5
    d_atk_roll = Dado.rolar(1, 6)
    d_atk_total = d_atk_roll + bonus_atk + dano_base_extra
    bonus_def = defensor.defesa // 6
    d_def_roll = Dado.rolar(1, 6)

    if defensor_ignora_def_bonus:
        def_bonus_used = 0
        d_def_total = d_def_roll
    else:
        def_bonus_used = bonus_def
        d_def_total = d_def_roll + def_bonus_used

    is_crit_roll = d_atk_roll == 6
    is_crit_buff = atacante.crit_chance_buff > 0
    is_crit = is_crit_roll or is_crit_buff
    dano_bruto = d_atk_total - d_def_total
    if dano_bruto < 0:
        dano_final = 0
    elif dano_bruto == 0:
        dano_final = 1
    else:
        dano_final = dano_bruto
    if is_crit and dano_final > 0:
        dano_final *= 2
    log_roll = (
        f" | Rolagens: ATK={d_atk_roll}+{bonus_atk}+{dano_base_extra}={d_atk_total} "
        f"vs DEF={d_def_roll}+{def_bonus_used}={d_def_total} "
    )
    return dano_final, log_roll, is_crit


class Personagem(ABC):
    def __init__(
        self,
        nome: str,
        vida_max: int,
        forca: int,
        defesa: int,
        velocidade: int,
        arma_inicial: Optional[Equipamento] = None,
    ) -> None:
        self.nome = nome
        self._vida_max_base = vida_max
        self._forca_base = forca
        self._defesa_base = defesa
        self._velocidade_base = velocidade

        self.equipamento: Dict[str, Optional[Equipamento]] = {
            "arma": None,
            "armadura": None,
            "bota": None,
            "luva": None,
        }
        self.inventario = Inventario()
        self.status_effects: Dict[str, StatusEffect] = {}
        self.crit_chance_buff = 0
        self.arma_elemento_fogo_duracao = 0
        self._auto_attr_index = 0

        if arma_inicial:
            self.equipar_item(arma_inicial, is_initial=True)

        self._vida = self.vida_max

        self.nivel = 1
        self.xp_atual = 0
        self.xp_proximo_nivel = 10
        self.pontos_atributos_livres = 0
        self.nivel_max = 20

    @property
    def forca(self) -> int:
        bonus = sum(e.modificadores.get("ATK", 0) for e in self.equipamento.values() if e)
        return self._forca_base + bonus

    @property
    def defesa(self) -> int:
        bonus = sum(e.modificadores.get("DEF", 0) for e in self.equipamento.values() if e)
        return self._defesa_base + bonus

    @property
    def velocidade(self) -> int:
        bonus = sum(e.modificadores.get("SPD", 0) for e in self.equipamento.values() if e)
        return self._velocidade_base + bonus

    @property
    def vida_max(self) -> int:
        bonus = sum(e.modificadores.get("HP", 0) for e in self.equipamento.values() if e)
        return self._vida_max_base + bonus

    @property
    def vida(self) -> int:
        return self._vida

    @vida.setter
    def vida(self, v: int) -> None:
        self._vida = max(0, min(v, self.vida_max))

    def _item_valor(self, item: Equipamento) -> Tuple[int, int]:
        preferencia = {
            "arma": "ATK",
            "armadura": "DEF",
            "bota": "SPD",
            "luva": "DEF",
        }
        preferido = preferencia.get(item.slot, "ATK")
        preferido_val = item.modificadores.get(preferido, 0)
        total = sum(item.modificadores.values())
        return preferido_val, total

    def equipar_item(
        self,
        item: Equipamento,
        battle: Optional["Batalha"] = None,
        is_initial: bool = False,
        auto: bool = False,
    ) -> bool:
        if not isinstance(item, Equipamento):
            return False
        slot = item.slot
        old_item = self.equipamento[slot]

        if is_initial:
            self.equipamento[slot] = item
            return True

        if auto:
            hp_before = self.vida
            hp_max_before = self.vida_max
            if old_item:
                prefer_new = self._item_valor(item)
                prefer_old = self._item_valor(old_item)
                if prefer_new <= prefer_old:
                    if battle:
                        battle.registrar(
                            f" {self.nome} guardou {item.nome} no inventário (melhor equipamento já equipado).",
                            "info",
                        )
                    return False
                self.inventario.adicionar(old_item)
            self.equipamento[slot] = item
            hp_max_after = self.vida_max
            self.vida = hp_before + (hp_max_after - hp_max_before)
            if battle:
                battle.registrar(
                    f" {self.nome} equipou automaticamente **{item.nome}** no slot {slot}.",
                    "equip",
                )
            return True

        if old_item:
            if battle:
                battle.registrar(
                    f" {self.nome} substituiu {old_item.nome} por {item.nome}.",
                    "equip",
                )
            self.inventario.adicionar(old_item)

        hp_before = self.vida
        hp_max_before = self.vida_max
        self.equipamento[slot] = item
        hp_diff = self.vida_max - hp_max_before
        self.vida = hp_before + hp_diff

        if battle:
            battle.registrar(f" {self.nome} equipou **{item.nome}** no slot {slot}!", "equip")
        return True

    def auto_equipar(self, battle: Optional["Batalha"] = None) -> None:
        for item in list(self.inventario.itens):
            if isinstance(item, Equipamento):
                if self.equipar_item(item, battle, auto=True):
                    self.inventario.remover(item)

    def receber_dano(self, dano_calculado: int) -> int:
        self.vida -= dano_calculado
        return dano_calculado

    def curar(self, valor_cura: int) -> int:
        antes = self.vida
        self.vida += valor_cura
        return self.vida - antes

    def esta_vivo(self) -> bool:
        return self.vida > 0

    def ganhar_xp(self, quantidade: int, battle: "Batalha") -> bool:
        if self.nivel >= self.nivel_max:
            return False
        antes = self.nivel
        self.xp_atual += quantidade
        battle.registrar(
            f" {self.nome} ganhou {quantidade} XP. ({self.xp_atual}/{self.xp_proximo_nivel})",
            "xp",
        )
        while self.xp_atual >= self.xp_proximo_nivel and self.nivel < self.nivel_max:
            self.upar_nivel(battle)
        if self.pontos_atributos_livres > 0:
            alocados = self.auto_distribuir_pontos()
            for attr in alocados:
                legivel = {
                    "_vida_max_base": "HP",
                    "_forca_base": "ATK",
                    "_defesa_base": "DEF",
                    "_velocidade_base": "SPD",
                }[attr]
                battle.registrar(
                    f" {self.nome} distribuiu automaticamente +1 ponto em {legivel}.",
                    "info",
                )
        return self.nivel > antes

    def upar_nivel(self, battle: "Batalha") -> None:
        self.nivel += 1
        self.xp_atual -= self.xp_proximo_nivel
        self.xp_proximo_nivel = self.nivel * 10
        self.pontos_atributos_livres += 5
        battle.registrar(f" {self.nome} subiu para o **NÍVEL {self.nivel}**!", "crit_hit")
        battle.registrar(" Recebeu **+5 Pontos** de Atributo Livres!", "crit_hit")

    def adicionar_ponto_atributo(self, attr_name: str, quantidade: int) -> None:
        if attr_name == "_vida_max_base":
            self._vida_max_base += quantidade
            self.vida += quantidade
        elif attr_name == "_forca_base":
            self._forca_base += quantidade
        elif attr_name == "_defesa_base":
            self._defesa_base += quantidade
        elif attr_name == "_velocidade_base":
            self._velocidade_base += quantidade
        self.pontos_atributos_livres -= quantidade

    def auto_distribuir_pontos(self) -> List[str]:
        ordem = ["_vida_max_base", "_forca_base", "_defesa_base", "_velocidade_base"]
        distribuidos: List[str] = []
        while self.pontos_atributos_livres > 0:
            attr = ordem[self._auto_attr_index % len(ordem)]
            self._auto_attr_index += 1
            self.adicionar_ponto_atributo(attr, 1)
            distribuidos.append(attr)
        return distribuidos

    def get_status(self) -> str:
        status_str = ", ".join(
            f"{s.nome} ({s.stacks}x, {s.duracao_restante}T)" for s in self.status_effects.values()
        )
        if status_str:
            status_str = f" | Status: {status_str}"
        equip_info = " | Equip:" + "".join(
            f" {slot[0].upper()}: {item.get_bonus_str() if item else '[Vazio]'}"
            for slot, item in self.equipamento.items()
        )
        return (
            f"[{self.nome} - NV:{self.nivel} ({self.xp_atual}/{self.xp_proximo_nivel}XP)] "
            f"HP: {self.vida}/{self.vida_max} | ATK: {self.forca} | DEF: {self.defesa} | SPD: {self.velocidade}"
            f"{equip_info}{status_str}"
        )

    def distribuir_xp_party(self, monstro: "Monstro", battle: "Batalha", party: List["Personagem"]) -> None:
        xp_total = 5
        xp_bonus = 3
        for heroi in party:
            if heroi.esta_vivo():
                xp_ganha = xp_total
                if heroi is self:
                    xp_ganha += xp_bonus
                heroi.ganhar_xp(xp_ganha, battle)
        battle.registrar(
            f" PARTY GAIN: {xp_total} XP base, {self.nome} (+{xp_bonus} bônus) pela vitória!",
            "xp",
        )
        item_drop = gerar_equipamento_aleatorio()
        self.inventario.adicionar(item_drop)
        battle.registrar(
            f" DROP: {monstro.nome} deixou cair **{item_drop.nome}**! Foi para o inventário de {self.nome}.",
            "item",
        )
        if self.equipar_item(item_drop, battle, auto=True):
            self.inventario.remover(item_drop)

    @abstractmethod
    def atacar(self, alvo: "Personagem", battle: "Batalha", party: List["Personagem"]) -> int:
        raise NotImplementedError

    def get_habilidades_ativas(self) -> Dict[str, str]:
        return {"classe": "Nenhuma", "arma": "Nenhuma"}


class Guerreiro(Personagem):
    def __init__(self, nome: str, stats: Dict[str, int]) -> None:
        super().__init__(nome, stats["HP"], stats["ATK"], stats["DEF"], stats["SPD"], arma_inicial=ESPADA_CURTA)

    def atacar(self, alvo: "Personagem", battle: "Batalha", party: List["Personagem"]) -> int:
        if not self.esta_vivo() or not alvo.esta_vivo():
            return 0
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(self, alvo)
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0:
            battle.registrar(
                f"{crit_str} [GUERREIRO] {self.nome} ataca {alvo.nome} ({log_roll}) causando {causado}!",
                "damage",
            )
        else:
            battle.registrar(
                f" [MISS] {self.nome} erra o golpe em {alvo.nome} ({log_roll}).",
                "miss",
            )
        if not alvo.esta_vivo() and isinstance(alvo, Monstro):
            self.distribuir_xp_party(alvo, battle, party)
        return causado

    def get_habilidades_ativas(self) -> Dict[str, str]:
        return {"classe": "Chamado do Líder", "arma": "Coronhada"}

    class ChamadoLiderBuff(StatusEffect):
        def __init__(self, atk: int, def_val: int) -> None:
            super().__init__("Chamado do Líder", 2)
            self.atk = atk
            self.def_val = def_val

    def usar_habilidade_classe(self, alvo: "Personagem", party: List["Personagem"], battle: "Batalha") -> int:
        if alvo not in party or not alvo.esta_vivo():
            battle.registrar(" Alvo inválido para Chamado do Líder.", "error")
            return 0
        buff_atk = Dado.rolar(1, 12)
        buff_def = Dado.rolar(1, 12)
        alvo._forca_base += buff_atk
        alvo._defesa_base += buff_def
        self.ChamadoLiderBuff(buff_atk, buff_def).aplicar(alvo, battle)
        battle.registrar(
            f" [CHAMADO] {self.nome} bufou {alvo.nome}: +{buff_atk} ATK, +{buff_def} DEF por 2T!",
            "skill",
        )
        return 1

    def coronhada(self, alvo: "Personagem", party: List["Personagem"], battle: "Batalha") -> int:
        if not alvo.esta_vivo():
            return 0
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(self, alvo, dano_base_extra=2)
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0:
            battle.registrar(
                f"{crit_str} [CORONHADA] {self.nome} usa Coronhada em {alvo.nome} ({log_roll}) causando {causado}!",
                "damage",
            )
        else:
            battle.registrar(
                f" [MISS] {self.nome} erra Coronhada em {alvo.nome} ({log_roll}).",
                "miss",
            )
        if not alvo.esta_vivo() and isinstance(alvo, Monstro):
            self.distribuir_xp_party(alvo, battle, party)
        return causado


class Mago(Personagem):
    def __init__(self, nome: str, stats: Dict[str, int]) -> None:
        super().__init__(nome, stats["HP"], stats["ATK"], stats["DEF"], stats["SPD"], arma_inicial=VARA_MOFADA)

    def atacar(self, alvo: "Personagem", battle: "Batalha", party: List["Personagem"]) -> int:
        if not self.esta_vivo() or not alvo.esta_vivo():
            return 0
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(
            self, alvo, defensor_ignora_def_bonus=True
        )
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0:
            battle.registrar(
                f"{crit_str} [MAGO] {self.nome} lança magia em {alvo.nome} ({log_roll}) causando {causado}!",
                "skill",
            )
        else:
            battle.registrar(
                f" [MISS] {self.nome} erra a magia em {alvo.nome} ({log_roll}).",
                "miss",
            )
        if not alvo.esta_vivo() and isinstance(alvo, Monstro):
            self.distribuir_xp_party(alvo, battle, party)
        return causado

    def get_habilidades_ativas(self) -> Dict[str, str]:
        return {"classe": "Bola de Fogo", "arma": "Ignis"}

    def usar_habilidade_classe(self, alvo: "Personagem", party: List["Personagem"], battle: "Batalha") -> int:
        if not alvo.esta_vivo():
            return 0
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(
            self,
            alvo,
            dano_base_extra=1,
            defensor_ignora_def_bonus=True,
        )
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0:
            battle.registrar(
                f"{crit_str} [BOLA FOGO] {self.nome} lança Bola de Fogo em {alvo.nome} ({log_roll}) causando {causado}!",
                "skill",
            )
            if Dado.rolar(1, 100) <= 30:
                Queimacao().aplicar(alvo, battle)
        else:
            battle.registrar(
                f" [MISS] {self.nome} erra a Bola de Fogo em {alvo.nome} ({log_roll}).",
                "miss",
            )
        if not alvo.esta_vivo() and isinstance(alvo, Monstro):
            self.distribuir_xp_party(alvo, battle, party)
        return causado

    def usar_habilidade_arma(self, alvo: "Personagem", party: List["Personagem"], battle: "Batalha") -> int:
        if alvo not in party or not alvo.equipamento.get("arma") or not alvo.esta_vivo():
            battle.registrar(" Alvo inválido ou sem arma para Ignis.", "error")
            return 0
        alvo.arma_elemento_fogo_duracao = 2
        battle.registrar(
            f" [IGNIS] {self.nome} imbuiu a arma de {alvo.nome} com Fogo por 2 turnos!",
            "skill",
        )
        return 1


class Arqueiro(Personagem):
    def __init__(self, nome: str, stats: Dict[str, int]) -> None:
        super().__init__(nome, stats["HP"], stats["ATK"], stats["DEF"], stats["SPD"], arma_inicial=ARCO_GALHOS)
        self.dano_passivo_extra = 1

    def atacar(self, alvo: "Personagem", battle: "Batalha", party: List["Personagem"]) -> int:
        if not self.esta_vivo() or not alvo.esta_vivo():
            return 0
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(self, alvo, dano_base_extra=self.dano_passivo_extra)
        is_double_shot = Dado.rolar(1, 10) <= 3
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0:
            battle.registrar(
                f"{crit_str} [ARQUEIRO] {self.nome} atira em {alvo.nome} ({log_roll}) causando {causado}!",
                "damage",
            )
        else:
            battle.registrar(
                f" [MISS] {self.nome} erra o tiro em {alvo.nome} ({log_roll}).",
                "miss",
            )
        dano_total = causado
        if is_double_shot and alvo.esta_vivo():
            battle.registrar(f" [COMBO] {self.nome} dispara um segundo tiro!", "crit_hit")
            dano_total += self.atacar(alvo, battle, party)
        if not alvo.esta_vivo() and isinstance(alvo, Monstro):
            self.distribuir_xp_party(alvo, battle, party)
        return dano_total

    def get_habilidades_ativas(self) -> Dict[str, str]:
        return {"classe": "Olho de Águia", "arma": "Nenhuma (Passiva)"}

    class OlhoAguiaBuff(StatusEffect):
        def __init__(self) -> None:
            super().__init__("Olho de Águia (100% CRIT)", 2)

    def usar_habilidade_classe(self, alvo: "Personagem", party: List["Personagem"], battle: "Batalha") -> int:
        if alvo not in party or not alvo.esta_vivo():
            battle.registrar(" Alvo inválido para Olho de Águia.", "error")
            return 0
        alvo.crit_chance_buff = 2
        self.OlhoAguiaBuff().aplicar(alvo, battle)
        battle.registrar(
            f" [OLHO ÁGUIA] {self.nome} bufou {alvo.nome}: 100% de chance de CRÍTICO por 2 rodadas!",
            "skill",
        )
        return 1

def gerar_status_soma_25_4_stats() -> Dict[str, int]:
    soma = 25
    cuts = sorted(random.sample(range(1, soma), 3))
    s1 = cuts[0]
    s2 = cuts[1] - cuts[0]
    s3 = cuts[2] - cuts[1]
    s4 = soma - cuts[2]
    stats = [s1, s2, s3, s4]
    random.shuffle(stats)
    return {
        "vida_max": stats[0] + 10,
        "forca": stats[1] + 5,
        "defesa": stats[2] + 5,
        "velocidade": stats[3] + 5,
    }


class Monstro(Personagem):
    def __init__(self, nome: str, forca_extra: int = 0) -> None:
        stats = gerar_status_soma_25_4_stats()
        super().__init__(
            nome,
            stats["vida_max"],
            stats["forca"] + forca_extra,
            stats["defesa"],
            stats["velocidade"],
        )
        self._forca_base += forca_extra

    def atacar(self, alvo: Personagem, battle: "Batalha", party: List[Personagem]) -> int:
        if not self.esta_vivo() or not alvo.esta_vivo():
            return 0
        dano_calculado, log_roll, is_crit = calcular_dano_rpg(self, alvo)
        causado = alvo.receber_dano(dano_calculado)
        crit_str = " [CRÍTICO] " if is_crit and dano_calculado > 0 else ""
        if causado > 0:
            battle.registrar(
                f"{crit_str} [INIMIGO] {self.nome} ataca {alvo.nome} ({log_roll}) causando {causado}!",
                "damage",
            )
        else:
            battle.registrar(
                f" [MISS] {self.nome} erra o ataque em {alvo.nome} ({log_roll}).",
                "miss",
            )
        if not alvo.esta_vivo():
            battle.registrar(f" {alvo.nome} foi derrotado por {self.nome}!", "damage")
        return causado

    def usar_habilidade_classe(self, alvo: Personagem, party: List[Personagem], battle: "Batalha") -> int:
        return 0

    def get_habilidades_ativas(self) -> Dict[str, str]:
        return {"classe": "Nenhuma", "arma": "Nenhuma"}


class Orc(Monstro):
    def __init__(self, i: int) -> None:
        super().__init__(f"Orc Brutal #{i}")


class Ogro(Monstro):
    def __init__(self, i: int) -> None:
        super().__init__(f"Ogro Pesado #{i}", forca_extra=5)


class Bruxa(Monstro):
    def __init__(self, i: int) -> None:
        super().__init__(f"Bruxa Sombria #{i}")

    def atacar(self, alvo: Personagem, battle: "Batalha", party: List[Personagem]) -> int:
        if Dado.rolar(1, 10) == 10:
            dano_magico = self.forca + Dado.rolar(5, 15)
            causado = alvo.receber_dano(dano_magico)
            battle.registrar(
                f" [MAGIA] {self.nome} lança Maldição Poderosa em {alvo.nome} causando {causado}!",
                "skill",
            )
            if not alvo.esta_vivo():
                battle.registrar(f" {alvo.nome} foi derrotado por {self.nome}!", "damage")
            return causado
        return super().atacar(alvo, battle, party)


def gerar_monstro_aleatorio_escalado(andar: int) -> Monstro:
    monster_types = [Orc, Ogro, Bruxa]
    monstro_cls = random.choice(monster_types)
    fator_escala = 1.3 ** (andar - 1)
    monstro = monstro_cls(andar)
    monstro._vida_max_base = math.ceil(monstro._vida_max_base * fator_escala)
    monstro._vida = monstro.vida_max
    monstro._forca_base = math.ceil(monstro._forca_base * fator_escala)
    monstro._defesa_base = math.ceil(monstro._defesa_base * fator_escala)
    monstro._velocidade_base = math.ceil(monstro._velocidade_base * fator_escala)
    tipo_andar = "Grupo"
    if andar == 10:
        tipo_andar = "Final"
    monstro.nome = f"Andar {andar} ({tipo_andar}) | {monstro.nome}"
    return monstro


class Batalha:
    def __init__(self, herois: List[Personagem], inimigos: List[Personagem]) -> None:
        self.herois = herois
        self.inimigos = inimigos
        self.ordem: List[Personagem] = herois + inimigos
        self.log: List[Tuple[str, str]] = []
        self.turno_idx = 0
        self.turno_ativo: Optional[Personagem] = None
        self.ordem.sort(key=lambda u: (u.velocidade, u.forca), reverse=True)
        self.registrar(f"Iniciativa: {[u.nome for u in self.ordem]}", "info")
        self.rodada = 1

    def registrar(self, texto: str, tag: str = "default") -> None:
        self.log.append((texto, tag))

    def unidades_vivas(self, grupo: List[Personagem]) -> List[Personagem]:
        return [u for u in grupo if u.esta_vivo()]

    def acaba(self) -> bool:
        herois_vivos = any(u.esta_vivo() for u in self.herois)
        inimigos_vivos = any(u.esta_vivo() for u in self.inimigos)
        return not (herois_vivos and inimigos_vivos)

    def aplicar_status_turn_start(self, unit: Personagem) -> bool:
        if "Queimacao" in unit.status_effects:
            q = unit.status_effects["Queimacao"]
            dano_queimacao = q.stacks * 1
            unit.vida -= dano_queimacao
            self.registrar(
                f" {unit.nome} sofre {dano_queimacao} de dano por Queimação ({q.stacks} acúmulos).",
                "fire",
            )
            if not unit.esta_vivo():
                self.registrar(f" {unit.nome} morreu devido a Queimação.", "damage")
                return False
        return True

    def gerenciar_status_pos_turno(self, unit: Personagem) -> None:
        if not unit.esta_vivo():
            return
        if unit.crit_chance_buff > 0:
            unit.crit_chance_buff -= 1
        if unit.arma_elemento_fogo_duracao > 0:
            unit.arma_elemento_fogo_duracao -= 1
        if "Chamado do Líder" in unit.status_effects:
            status = unit.status_effects["Chamado do Líder"]
            status.duracao_restante -= 1
            if status.duracao_restante <= 0:
                unit._forca_base -= status.atk
                unit._defesa_base -= status.def_val
                self.registrar(f" Chamado do Líder em {unit.nome} terminou e reverteu o buff.", "info")
                del unit.status_effects["Chamado do Líder"]
        if "Olho de Águia (100% CRIT)" in unit.status_effects:
            status = unit.status_effects["Olho de Águia (100% CRIT)"]
            status.duracao_restante -= 1
            if status.duracao_restante <= 0:
                unit.crit_chance_buff = 0
                self.registrar(f" Olho de Águia em {unit.nome} terminou.", "info")
                del unit.status_effects["Olho de Águia (100% CRIT)"]
        if "Queimacao" in unit.status_effects:
            q = unit.status_effects["Queimacao"]
            q.duracao_restante -= 1
            if q.duracao_restante <= 0:
                self.registrar(f" Efeito Queimação em {unit.nome} terminou.", "info")
                del unit.status_effects["Queimacao"]

    def proximo_turno(self) -> Optional[str]:
        if self.acaba():
            return None
        while True:
            if not self.ordem:
                return None
            if self.turno_idx >= len(self.ordem):
                self.rodada += 1
                self.ordem = self.unidades_vivas(self.herois) + self.unidades_vivas(self.inimigos)
                self.ordem.sort(key=lambda u: (u.velocidade, u.forca), reverse=True)
                self.turno_idx = 0
                if not self.ordem:
                    return None
                self.registrar("--- Nova Rodada Iniciada ---", "turn_start")
            self.turno_ativo = self.ordem[self.turno_idx]
            self.turno_idx += 1
            if not self.turno_ativo.esta_vivo():
                continue
            if not self.aplicar_status_turn_start(self.turno_ativo):
                self.gerenciar_status_pos_turno(self.turno_ativo)
                if self.acaba():
                    return None
                continue
            if self.turno_ativo in self.herois:
                return "Jogador"
            self.ai_turn(self.turno_ativo)
            self.gerenciar_status_pos_turno(self.turno_ativo)
            if self.acaba():
                return None

    def ai_turn(self, unit: Personagem) -> None:
        vivos = self.unidades_vivas(self.herois)
        if not vivos:
            return
        alvo = random.choice(vivos)
        unit.atacar(alvo, self, self.herois)


ALLY_CLASS_SKILLS = {"Chamado do Líder", "Olho de Águia"}
ENEMY_CLASS_SKILLS = {"Bola de Fogo"}
ALLY_WEAPON_SKILLS = {"Ignis"}
ENEMY_WEAPON_SKILLS = {"Coronhada"}

LOG_COLORS = {
    "default": "#f8f8f2",
    "info": "#8be9fd",
    "damage": "#ff5555",
    "miss": "#6272a4",
    "skill": "#bd93f9",
    "crit_hit": "#ff79c6",
    "fire": "#ffb86c",
    "heal": "#50fa7b",
    "xp": "#f1fa8c",
    "item": "#69ff94",
    "equip": "#ffe066",
    "error": "#ff6b6b",
    "turn_start": "#94b3fd",
}


class GameGUI:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Heroes RPG - GUI Edition")
        self.root.configure(bg="#1b1b1b")
        self.root.geometry("1024x640")
        self.root.minsize(900, 600)

        self.party: List[Personagem] = []
        self.current_floor = 1
        self.battle: Optional[Batalha] = None
        self.log_position = 0
        self.active_hero: Optional[Personagem] = None

        self.hero_vars: Dict[Personagem, tk.StringVar] = {}
        self.hero_buttons: Dict[Personagem, tk.Button] = {}
        self.enemy_target_var = tk.StringVar()
        self.enemy_menu: Optional[tk.OptionMenu] = None
        self.log_text: Optional[tk.Text] = None
        self.enemies_container: Optional[tk.Frame] = None
        self.btn_attack: Optional[tk.Button] = None
        self.btn_class: Optional[tk.Button] = None
        self.btn_weapon: Optional[tk.Button] = None
        self.btn_heal: Optional[tk.Button] = None
        self.btn_pass: Optional[tk.Button] = None
        self.turn_label: Optional[tk.Label] = None
        self.floor_label: Optional[tk.Label] = None
        self.heroes_frame: Optional[tk.Frame] = None
        self.main_frame: Optional[tk.Frame] = None
        self.sidebar: Optional[tk.Frame] = None
        self.creation_frame: Optional[tk.Frame] = None
        self.preview_stats: Dict[str, int] = {}
        self.player_name_var = tk.StringVar()
        self.player_class_var = tk.StringVar(value="Guerreiro")
        self.preview_text_var = tk.StringVar()

        self._build_start_screen()

    def _build_start_screen(self) -> None:
        self.creation_frame = tk.Frame(self.root, bg="#1b1b1b", padx=30, pady=30)
        self.creation_frame.pack(fill=tk.BOTH, expand=True)

        titulo = tk.Label(
            self.creation_frame,
            text="Criação de Personagem",
            bg="#1b1b1b",
            fg="#f8f8f2",
            font=("Segoe UI", 20, "bold"),
        )
        titulo.pack(pady=(0, 20))

        descricao = tk.Label(
            self.creation_frame,
            text=(
                "Escolha o nome do herói principal e a classe antes de iniciar a aventura.\n"
                "Os aliados restantes serão sorteados automaticamente."
            ),
            bg="#1b1b1b",
            fg="#f8f8f2",
            justify=tk.CENTER,
            font=("Segoe UI", 11),
        )
        descricao.pack(pady=(0, 20))

        form_frame = tk.Frame(self.creation_frame, bg="#2b2b2b", padx=20, pady=20, relief=tk.RIDGE, bd=2)
        form_frame.pack(pady=10, fill=tk.X)

        nome_label = tk.Label(
            form_frame,
            text="Nome do Herói:",
            bg="#2b2b2b",
            fg="#f8f8f2",
            font=("Segoe UI", 11, "bold"),
        )
        nome_label.grid(row=0, column=0, sticky="w")

        nome_entry = tk.Entry(
            form_frame,
            textvariable=self.player_name_var,
            font=("Segoe UI", 11),
            width=28,
        )
        nome_entry.grid(row=0, column=1, padx=(10, 0), sticky="w")
        nome_entry.focus_set()

        classe_label = tk.Label(
            form_frame,
            text="Classe:",
            bg="#2b2b2b",
            fg="#f8f8f2",
            font=("Segoe UI", 11, "bold"),
        )
        classe_label.grid(row=1, column=0, pady=(15, 0), sticky="nw")

        classes_frame = tk.Frame(form_frame, bg="#2b2b2b")
        classes_frame.grid(row=1, column=1, pady=(10, 0), sticky="w")

        class_options = [
            ("Guerreiro", "Especialista em combate corpo a corpo."),
            ("Mago", "Foco em magia com dano constante."),
            ("Arqueiro", "Ataques à distância e chance de combos."),
        ]

        for idx, (classe, texto) in enumerate(class_options):
            radio = tk.Radiobutton(
                classes_frame,
                text=f"{classe} - {texto}",
                value=classe,
                variable=self.player_class_var,
                command=self._gerar_stats_preview,
                bg="#2b2b2b",
                fg="#f8f8f2",
                selectcolor="#44475a",
                anchor="w",
                font=("Segoe UI", 10),
                width=42,
                justify=tk.LEFT,
            )
            radio.grid(row=idx, column=0, sticky="w", pady=2)

        self.preview_text_var.set("")
        self.preview_label = tk.Label(
            self.creation_frame,
            textvariable=self.preview_text_var,
            bg="#1b1b1b",
            fg="#f8f8f2",
            font=("Consolas", 12),
            justify=tk.CENTER,
        )
        self.preview_label.pack(pady=20)

        botoes_frame = tk.Frame(self.creation_frame, bg="#1b1b1b")
        botoes_frame.pack(pady=10)

        reroll_btn = tk.Button(
            botoes_frame,
            text="Rolar Novos Status",
            command=self._gerar_stats_preview,
            bg="#44475a",
            fg="#f8f8f2",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=8,
        )
        reroll_btn.grid(row=0, column=0, padx=10)

        iniciar_btn = tk.Button(
            botoes_frame,
            text="Começar Aventura",
            command=self._iniciar_aventura,
            bg="#50fa7b",
            fg="#1b1b1b",
            font=("Segoe UI", 11, "bold"),
            padx=20,
            pady=8,
        )
        iniciar_btn.grid(row=0, column=1, padx=10)

        self._gerar_stats_preview()

    def _gerar_stats_preview(self) -> None:
        base = gerar_status_base_aleatorio()
        self.preview_stats = distribuir_pontos_aleatorio(base, 15)
        stats_txt = (
            f"Status Iniciais | Classe {self.player_class_var.get()}\n"
            f"HP: {self.preview_stats['HP']}  ATK: {self.preview_stats['ATK']}  "
            f"DEF: {self.preview_stats['DEF']}  SPD: {self.preview_stats['SPD']}"
        )
        self.preview_text_var.set(stats_txt)

    def _preparar_heroi_inicial(self, heroi: Personagem) -> None:
        heroi.inventario.adicionar(PocaoCura())
        heroi.inventario.adicionar(PocaoCura())
        heroi.auto_equipar()

    def _iniciar_aventura(self) -> None:
        nome = self.player_name_var.get().strip()
        if not nome:
            messagebox.showinfo("Criação", "Digite um nome para o herói principal.")
            return
        classe_escolhida = self.player_class_var.get()
        classe_map = {
            "Guerreiro": Guerreiro,
            "Mago": Mago,
            "Arqueiro": Arqueiro,
        }
        classe_principal = classe_map.get(classe_escolhida, Guerreiro)
        stats_heroi = self.preview_stats or distribuir_pontos_aleatorio(gerar_status_base_aleatorio(), 15)
        heroi_principal = classe_principal(nome, stats_heroi)
        self._preparar_heroi_inicial(heroi_principal)

        party: List[Personagem] = [heroi_principal]
        nomes_padrao = {
            Guerreiro: "Aliado Guerreiro",
            Mago: "Aliado Mago",
            Arqueiro: "Aliado Arqueiro",
        }
        for classe, nome_padrao in nomes_padrao.items():
            if classe is classe_principal:
                continue
            stats_aliado = distribuir_pontos_aleatorio(gerar_status_base_aleatorio(), 10)
            aliado = classe(nome_padrao, stats_aliado)
            self._preparar_heroi_inicial(aliado)
            party.append(aliado)

        self.party = party
        self.current_floor = 1

        if self.creation_frame:
            self.creation_frame.destroy()
            self.creation_frame = None

        self._build_main_ui()
        self._start_new_floor()

    def _build_main_ui(self) -> None:
        self.header = tk.Frame(self.root, bg="#1b1b1b")
        self.header.pack(fill=tk.X, padx=10, pady=10)

        self.floor_label = tk.Label(
            self.header,
            text="",
            bg="#1b1b1b",
            fg="#f8f8f2",
            font=("Segoe UI", 16, "bold"),
        )
        self.floor_label.pack(side=tk.LEFT)

        self.turn_label = tk.Label(
            self.header,
            text="",
            bg="#1b1b1b",
            fg="#f8f8f2",
            font=("Segoe UI", 12, "bold"),
        )
        self.turn_label.pack(side=tk.RIGHT)

        self.heroes_frame = tk.Frame(self.root, bg="#2b2b2b", relief=tk.RIDGE, bd=2)
        self.heroes_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.hero_vars.clear()
        self.hero_buttons.clear()
        for heroi in self.party:
            var = tk.StringVar()
            frame = tk.Frame(self.heroes_frame, bg="#2b2b2b", padx=10, pady=10)
            frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            label = tk.Label(
                frame,
                textvariable=var,
                bg="#2b2b2b",
                fg="#f8f8f2",
                justify=tk.LEFT,
                font=("Consolas", 10),
                anchor="w",
            )
            label.pack(fill=tk.BOTH)
            btn_inv = tk.Button(
                frame,
                text="Abrir Inventário",
                command=lambda h=heroi: self._abrir_inventario(h),
                bg="#44475a",
                fg="#f8f8f2",
                font=("Segoe UI", 9, "bold"),
                pady=4,
            )
            btn_inv.pack(pady=(8, 0))
            self.hero_vars[heroi] = var
            self.hero_buttons[heroi] = btn_inv

        self.main_frame = tk.Frame(self.root, bg="#1b1b1b")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        self.log_text = tk.Text(
            self.main_frame,
            bg="#1e1e1e",
            fg="#f8f8f2",
            state=tk.DISABLED,
            wrap=tk.WORD,
            font=("Consolas", 10),
        )
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        for tag, color in LOG_COLORS.items():
            self.log_text.tag_configure(tag, foreground=color)

        self.sidebar = tk.Frame(self.main_frame, bg="#252525", width=220)
        self.sidebar.pack(side=tk.RIGHT, fill=tk.Y)

        self.enemy_header = tk.Label(
            self.sidebar,
            text="INIMIGOS",
            bg="#252525",
            fg="#f8f8f2",
            font=("Segoe UI", 12, "bold"),
        )
        self.enemy_header.pack(pady=(10, 5))

        self.enemies_container = tk.Frame(self.sidebar, bg="#252525")
        self.enemies_container.pack(fill=tk.BOTH, expand=True, padx=5)

        self.controls = tk.Frame(self.root, bg="#1b1b1b")
        self.controls.pack(fill=tk.X, padx=10, pady=(0, 10))

        self.enemy_target_var = tk.StringVar()

        self.enemy_menu = tk.OptionMenu(self.controls, self.enemy_target_var, "")
        self.enemy_menu.configure(bg="#44475a", fg="#f8f8f2", highlightthickness=0)
        self.enemy_menu.pack(side=tk.RIGHT, padx=5)

        tk.Label(
            self.controls,
            text="Escolha o Alvo Inimigo:",
            bg="#1b1b1b",
            fg="#f8f8f2",
        ).pack(side=tk.RIGHT)

        self.btn_pass = tk.Button(
            self.controls,
            text="⏭ PASSAR",
            command=self._passar_turno,
            bg="#44475a",
            fg="#f8f8f2",
            font=("Segoe UI", 11, "bold"),
            width=12,
        )
        self.btn_pass.pack(side=tk.LEFT, padx=5)

        self.btn_heal = tk.Button(
            self.controls,
            text="💚 CURAR (Poção)",
            command=self._curar,
            bg="#3aa675",
            fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            width=15,
        )
        self.btn_heal.pack(side=tk.LEFT, padx=5)

        self.btn_attack = tk.Button(
            self.controls,
            text="🗡 [A] Atacar",
            command=self._atacar,
            bg="#ff9f43",
            fg="#1b1b1b",
            font=("Segoe UI", 11, "bold"),
            width=12,
        )
        self.btn_attack.pack(side=tk.LEFT, padx=5)

        self.btn_class = tk.Button(
            self.controls,
            text="🔥 [C] Habilidade Classe",
            command=self._habilidade_classe,
            bg="#ff5555",
            fg="#f8f8f2",
            font=("Segoe UI", 11, "bold"),
            width=18,
        )
        self.btn_class.pack(side=tk.LEFT, padx=5)

        self.btn_weapon = tk.Button(
            self.controls,
            text="⚔ [W] Habilidade Arma",
            command=self._habilidade_arma,
            bg="#6272a4",
            fg="#f8f8f2",
            font=("Segoe UI", 11, "bold"),
            width=18,
        )
        self.btn_weapon.pack(side=tk.LEFT, padx=5)

    def _update_option_menu(self, menu: tk.OptionMenu, variable: tk.StringVar, options: List[str]) -> None:
        menu["menu"].delete(0, "end")
        if options:
            for option in options:
                menu["menu"].add_command(label=option, command=tk._setit(variable, option))
            variable.set(options[0])
        else:
            menu["menu"].add_command(label="-", command=tk._setit(variable, ""))
            variable.set("")

    def _abrir_inventario(self, heroi: Personagem) -> None:
        janela = tk.Toplevel(self.root)
        janela.title(f"Inventário de {heroi.nome}")
        janela.configure(bg="#1e1e1e")
        janela.geometry("420x470")
        janela.resizable(False, False)
        janela.transient(self.root)

        stats_var = tk.StringVar()
        stats_label = tk.Label(
            janela,
            textvariable=stats_var,
            bg="#1e1e1e",
            fg="#f8f8f2",
            font=("Consolas", 11, "bold"),
            justify=tk.CENTER,
        )
        stats_label.pack(pady=(15, 5))

        equipados_var = tk.StringVar()
        equipados_label = tk.Label(
            janela,
            textvariable=equipados_var,
            bg="#1e1e1e",
            fg="#f8f8f2",
            font=("Consolas", 10),
            justify=tk.LEFT,
            anchor="w",
        )
        equipados_label.pack(fill=tk.X, padx=10)

        potion_var = tk.StringVar()
        potion_label = tk.Label(
            janela,
            textvariable=potion_var,
            bg="#1e1e1e",
            fg="#f8f8f2",
            font=("Segoe UI", 10, "italic"),
            anchor="w",
        )
        potion_label.pack(fill=tk.X, padx=10, pady=(0, 5))

        list_frame = tk.Frame(janela, bg="#1e1e1e")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(5, 10))

        inventory_items: List[Item] = []
        listbox = tk.Listbox(
            list_frame,
            bg="#2b2b2b",
            fg="#f8f8f2",
            font=("Consolas", 10),
            selectbackground="#6272a4",
            activestyle="none",
        )
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.configure(yscrollcommand=scrollbar.set)

        detail_var = tk.StringVar(value="Selecione um item para detalhes.")
        detail_label = tk.Label(
            janela,
            textvariable=detail_var,
            bg="#1e1e1e",
            fg="#f8f8f2",
            font=("Consolas", 10),
            justify=tk.LEFT,
            wraplength=380,
            anchor="w",
        )
        detail_label.pack(fill=tk.X, padx=10)

        botoes = tk.Frame(janela, bg="#1e1e1e")
        botoes.pack(pady=(5, 15))

        equip_button = tk.Button(
            botoes,
            text="Equipar Selecionado",
            state=tk.DISABLED,
            bg="#50fa7b",
            fg="#1b1b1b",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5,
        )
        equip_button.pack(side=tk.LEFT, padx=5)

        fechar_button = tk.Button(
            botoes,
            text="Fechar",
            command=janela.destroy,
            bg="#ff5555",
            fg="#f8f8f2",
            font=("Segoe UI", 10, "bold"),
            padx=10,
            pady=5,
        )
        fechar_button.pack(side=tk.LEFT, padx=5)

        def descricao_item(item: Item) -> str:
            if isinstance(item, Equipamento):
                return (
                    f"{item.nome}\n"
                    f"Slot: {item.slot.capitalize()} | Bônus: {item.get_bonus_str()}"
                )
            if isinstance(item, PocaoCura):
                return f"{item.nome}\nRecupera 1d12 HP quando utilizada."
            return item.nome

        def atualizar_listas() -> None:
            stats_var.set(
                f"HP {heroi.vida}/{heroi.vida_max} | ATK {heroi.forca} | DEF {heroi.defesa} | SPD {heroi.velocidade}"
            )
            equip_lines = []
            for slot in ("arma", "armadura", "bota", "luva"):
                item = heroi.equipamento.get(slot)
                if item:
                    equip_lines.append(f"{slot.capitalize()}: {item.nome} {item.get_bonus_str()}")
                else:
                    equip_lines.append(f"{slot.capitalize()}: [Vazio]")
            equipados_var.set("\n".join(equip_lines))
            potion_var.set(f"Poções de Cura: {heroi.inventario.contar(PocaoCura)}")

            inventory_items.clear()
            listbox.delete(0, tk.END)
            for item in heroi.inventario.listar():
                inventory_items.append(item)
                texto = item.nome
                if isinstance(item, Equipamento):
                    texto += f" ({item.slot.capitalize()} {item.get_bonus_str()})"
                listbox.insert(tk.END, texto)

            if not inventory_items:
                listbox.insert(tk.END, "Inventário vazio.")
                listbox.itemconfig(listbox.size() - 1, fg="#6272a4")
            detail_var.set("Selecione um item para detalhes.")
            equip_button.config(state=tk.DISABLED)

        def on_select(event: Optional[tk.Event] = None) -> None:
            if not listbox.curselection():
                detail_var.set("Selecione um item para detalhes.")
                equip_button.config(state=tk.DISABLED)
                return
            index = listbox.curselection()[0]
            if index >= len(inventory_items):
                detail_var.set("Sem itens para inspecionar.")
                equip_button.config(state=tk.DISABLED)
                return
            item = inventory_items[index]
            detail_var.set(descricao_item(item))
            if isinstance(item, Equipamento):
                equip_button.config(state=tk.NORMAL)
            else:
                equip_button.config(state=tk.DISABLED)

        def equipar_item_selecionado() -> None:
            if not listbox.curselection():
                return
            index = listbox.curselection()[0]
            if index >= len(inventory_items):
                return
            item = inventory_items[index]
            if not isinstance(item, Equipamento):
                messagebox.showinfo("Inventário", "Apenas equipamentos podem ser equipados.")
                return
            if heroi.equipar_item(item):
                heroi.inventario.remover(item)
                mensagem = f" {heroi.nome} equipou **{item.nome}** através do inventário."
                if self.battle:
                    self.battle.registrar(mensagem, "equip")
                    self._append_log()
                else:
                    messagebox.showinfo("Equipamento", mensagem.strip())
                atualizar_listas()
                self._update_heroes_panel()
            else:
                messagebox.showinfo(
                    "Inventário",
                    "O herói preferiu manter o equipamento atual.",
                )

        equip_button.config(command=equipar_item_selecionado)
        listbox.bind("<<ListboxSelect>>", on_select)

        atualizar_listas()

    def _start_new_floor(self) -> None:
        vivos = [h for h in self.party if h.esta_vivo()]
        if not vivos:
            self._mostrar_derrota()
            return
        inimigos = [gerar_monstro_aleatorio_escalado(self.current_floor) for _ in range(random.randint(1, 3))]
        self.battle = Batalha(self.party, inimigos)
        self.log_position = 0
        self._append_log()
        self._update_heroes_panel()
        self._update_enemies_panel()
        self.floor_label.config(text=f"Andar {self.current_floor}")
        self._prosseguir_turnos()

    def _append_log(self) -> None:
        if not self.battle:
            return
        while self.log_position < len(self.battle.log):
            texto, tag = self.battle.log[self.log_position]
            self.log_position += 1
            self.log_text.configure(state=tk.NORMAL)
            self.log_text.insert(tk.END, texto + "\n", tag if tag in LOG_COLORS else "default")
            self.log_text.configure(state=tk.DISABLED)
            self.log_text.see(tk.END)

    def _update_heroes_panel(self) -> None:
        for heroi, var in self.hero_vars.items():
            status = (
                f"{heroi.nome} ({heroi.__class__.__name__})\n"
                f"HP: {heroi.vida}/{heroi.vida_max} | NV {heroi.nivel} ({heroi.xp_atual}/{heroi.xp_proximo_nivel})\n"
                f"ATK {heroi.forca} | DEF {heroi.defesa} | SPD {heroi.velocidade}\n"
                f"Poções: {heroi.inventario.contar(PocaoCura)}"
            )
            if heroi.status_effects:
                efeitos = ", ".join(
                    f"{status_nome} ({status.duracao_restante}T)" for status_nome, status in heroi.status_effects.items()
                )
                status += f"\nStatus: {efeitos}"
            if not heroi.esta_vivo():
                status += "\n**Derrotado**"
            var.set(status)
            botao = self.hero_buttons.get(heroi)
            if botao:
                botao.config(state=tk.NORMAL if heroi.esta_vivo() else tk.DISABLED)

    def _update_enemies_panel(self) -> None:
        if not self.battle:
            return
        for widget in self.enemies_container.winfo_children():
            widget.destroy()
        vivos = [i for i in self.battle.inimigos if i.esta_vivo()]
        if not vivos:
            label = tk.Label(
                self.enemies_container,
                text="Todos derrotados!",
                bg="#252525",
                fg="#f8f8f2",
                font=("Segoe UI", 10, "italic"),
            )
            label.pack(anchor="w", padx=5, pady=2)
        else:
            for inimigo in vivos:
                text = (
                    f"{inimigo.nome}\n"
                    f"HP: {inimigo.vida}/{inimigo.vida_max} | ATK {inimigo.forca} | DEF {inimigo.defesa} | SPD {inimigo.velocidade}"
                )
                label = tk.Label(
                    self.enemies_container,
                    text=text,
                    justify=tk.LEFT,
                    bg="#252525",
                    fg="#f8f8f2",
                    font=("Consolas", 9),
                    anchor="w",
                )
                label.pack(fill=tk.X, padx=5, pady=4)
        enemy_names = [i.nome for i in vivos]
        self._update_option_menu(self.enemy_menu, self.enemy_target_var, enemy_names)

    def _prosseguir_turnos(self) -> None:
        if not self.battle:
            return
        resultado = self.battle.proximo_turno()
        self._append_log()
        self._update_heroes_panel()
        self._update_enemies_panel()
        if self.battle.acaba():
            self._finalizar_andar()
            return
        if resultado == "Jogador":
            self.active_hero = self.battle.turno_ativo
            self.turn_label.config(text=f"Turno de {self.active_hero.nome}")
            self._configurar_botoes_turno()
        else:
            self.root.after(400, self._prosseguir_turnos)

    def _configurar_botoes_turno(self) -> None:
        if not self.active_hero or not all(
            (self.btn_attack, self.btn_class, self.btn_weapon, self.btn_heal, self.btn_pass)
        ):
            return
        habilidades = self.active_hero.get_habilidades_ativas()
        classe = habilidades.get("classe", "Nenhuma")
        arma = habilidades.get("arma", "Nenhuma")
        self.btn_class.config(
            state=tk.NORMAL if classe != "Nenhuma" else tk.DISABLED,
            text=f"🔥 [C] {classe}",
        )
        self.btn_weapon.config(
            state=tk.NORMAL if arma != "Nenhuma (Passiva)" and arma != "Nenhuma" else tk.DISABLED,
            text=f"⚔ [W] {arma}",
        )
        self.btn_attack.config(state=tk.NORMAL, text="🗡 [A] Atacar")
        self.btn_heal.config(state=tk.NORMAL)
        self.btn_pass.config(state=tk.NORMAL)

    def _desabilitar_acoes(self) -> None:
        for btn in (self.btn_attack, self.btn_class, self.btn_weapon, self.btn_heal, self.btn_pass):
            if btn:
                btn.config(state=tk.DISABLED)

    def _obter_inimigo_alvo(self) -> Optional[Personagem]:
        if not self.battle:
            return None
        nome = self.enemy_target_var.get()
        for inimigo in self.battle.inimigos:
            if inimigo.nome == nome and inimigo.esta_vivo():
                return inimigo
        return None

    def _selecionar_aliado(self, titulo: str) -> Optional[Personagem]:
        vivos = [h for h in self.party if h.esta_vivo()]
        if not vivos:
            return None
        if len(vivos) == 1:
            return vivos[0]

        selecionado: List[Optional[Personagem]] = [None]

        dialog = tk.Toplevel(self.root)
        dialog.title(titulo)
        dialog.configure(bg="#1e1e1e")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog,
            text="Escolha um aliado:",
            bg="#1e1e1e",
            fg="#f8f8f2",
            font=("Segoe UI", 11, "bold"),
        ).pack(padx=20, pady=(20, 10))

        lista = tk.Frame(dialog, bg="#1e1e1e")
        lista.pack(padx=20, pady=(0, 20))

        for heroi in vivos:
            texto = f"{heroi.nome} | HP {heroi.vida}/{heroi.vida_max}"

            def escolher(h: Personagem = heroi) -> None:
                selecionado[0] = h
                dialog.destroy()

            btn = tk.Button(
                lista,
                text=texto,
                command=escolher,
                bg="#44475a",
                fg="#f8f8f2",
                font=("Segoe UI", 10, "bold"),
                width=32,
                pady=4,
            )
            btn.pack(pady=3, fill=tk.X)

        cancel_btn = tk.Button(
            dialog,
            text="Cancelar",
            command=dialog.destroy,
            bg="#6c757d",
            fg="#f8f8f2",
            font=("Segoe UI", 10, "bold"),
            width=12,
        )
        cancel_btn.pack(pady=(0, 20))

        self.root.wait_window(dialog)
        return selecionado[0]

    def _atacar(self) -> None:
        if not self.active_hero or not self.battle:
            return
        alvo = self._obter_inimigo_alvo()
        if not alvo:
            messagebox.showinfo("Ação inválida", "Nenhum inimigo selecionado.")
            return
        self.active_hero.atacar(alvo, self.battle, self.party)
        self._apos_acao_jogador()

    def _habilidade_classe(self) -> None:
        if not self.active_hero or not self.battle:
            return
        habilidades = self.active_hero.get_habilidades_ativas()
        skill = habilidades.get("classe", "Nenhuma")
        if skill in ALLY_CLASS_SKILLS:
            alvo = self._selecionar_aliado(f"{skill} - Escolher Aliado")
            if not alvo:
                messagebox.showinfo("Ação inválida", "Nenhum aliado foi selecionado.")
                return
            self.active_hero.usar_habilidade_classe(alvo, self.party, self.battle)
        elif skill in ENEMY_CLASS_SKILLS:
            alvo = self._obter_inimigo_alvo()
            if not alvo:
                messagebox.showinfo("Ação inválida", "Selecione um inimigo para a habilidade de classe.")
                return
            self.active_hero.usar_habilidade_classe(alvo, self.party, self.battle)
        self._apos_acao_jogador()

    def _habilidade_arma(self) -> None:
        if not self.active_hero or not self.battle:
            return
        habilidades = self.active_hero.get_habilidades_ativas()
        skill = habilidades.get("arma", "Nenhuma")
        if skill in ALLY_WEAPON_SKILLS:
            alvo = self._selecionar_aliado(f"{skill} - Escolher Aliado")
            if not alvo:
                messagebox.showinfo("Ação inválida", "Nenhum aliado foi selecionado.")
                return
            self.active_hero.usar_habilidade_arma(alvo, self.party, self.battle)
        elif skill in ENEMY_WEAPON_SKILLS:
            alvo = self._obter_inimigo_alvo()
            if not alvo:
                messagebox.showinfo("Ação inválida", "Selecione um inimigo para a habilidade de arma.")
                return
            if isinstance(self.active_hero, Guerreiro):
                self.active_hero.coronhada(alvo, self.party, self.battle)
        self._apos_acao_jogador()

    def _curar(self) -> None:
        if not self.active_hero or not self.battle:
            return
        if self.active_hero.inventario.contar(PocaoCura) <= 0:
            messagebox.showinfo("Sem poções", f"{self.active_hero.nome} não possui poções de cura.")
            return
        pocao = next(item for item in self.active_hero.inventario.itens if isinstance(item, PocaoCura))
        pocao.usar(self.active_hero, self.battle)
        self.active_hero.inventario.remover(pocao)
        self._apos_acao_jogador()

    def _passar_turno(self) -> None:
        if not self.active_hero or not self.battle:
            return
        self.battle.registrar(f" {self.active_hero.nome} passa o turno.", "info")
        self._apos_acao_jogador()

    def _apos_acao_jogador(self) -> None:
        if not self.active_hero or not self.battle:
            return
        self._desabilitar_acoes()
        self.battle.gerenciar_status_pos_turno(self.active_hero)
        self._append_log()
        self._update_heroes_panel()
        self._update_enemies_panel()
        if self.battle.acaba():
            self._finalizar_andar()
        else:
            self.root.after(400, self._prosseguir_turnos)

    def _finalizar_andar(self) -> None:
        if not self.battle:
            return
        self._append_log()
        vivos = [h for h in self.party if h.esta_vivo()]
        if not vivos:
            self._mostrar_derrota()
            return
        for heroi in vivos:
            curado = heroi.curar(heroi.vida_max // 4)
            if curado > 0:
                self.battle.registrar(
                    f" {heroi.nome} recupera {curado} HP após a batalha (descanso).",
                    "heal",
                )
        self._append_log()
        self._update_heroes_panel()
        if self.current_floor >= 10:
            self._mostrar_vitoria()
            return
        self.current_floor += 1
        self.root.after(800, self._start_new_floor)

    def _mostrar_vitoria(self) -> None:
        self._desabilitar_acoes()
        messagebox.showinfo("Vitória!", "Parabéns! Você derrotou todos os 10 andares de monstros!")
        self.turn_label.config(text="Aventura concluída!")

    def _mostrar_derrota(self) -> None:
        self._desabilitar_acoes()
        messagebox.showinfo("Derrota", "Sua party foi derrotada. Tente novamente!")
        self.turn_label.config(text="Party derrotada.")

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    jogo = GameGUI()
    jogo.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - captura global para feedback visual
        messagebox.showerror("Erro fatal", f"Ocorreu um erro fatal: {exc}")
        raise