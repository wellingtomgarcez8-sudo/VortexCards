from __future__ import annotations
import pygame
from vortexcards.game.engine import GameEngine, RuleError
from vortexcards.game.models import PlayerState, CardKind, CardColor
from vortexcards.ai.bot import BotController

BG=(10,12,24); PANEL=(23,25,48); TEXT=(235,239,255); MUTED=(150,158,190)
ACCENT=(135,78,255); COLORS={CardColor.RED:(220,65,80),CardColor.BLUE:(55,120,235),CardColor.GREEN:(50,175,110),CardColor.YELLOW:(235,190,55)}

class App:
    def __init__(self):
        pygame.init(); pygame.display.set_caption("Vortex Cards")
        self.screen=pygame.display.set_mode((1280,720), pygame.RESIZABLE)
        self.clock=pygame.time.Clock(); self.font=pygame.font.SysFont("arial",24); self.big=pygame.font.SysFont("arial",54,bold=True)
        self.running=True; self.scene="menu"; self.engine=None; self.human_id="human"; self.bot=BotController("normal")

    def run(self):
        while self.running:
            for e in pygame.event.get():
                if e.type==pygame.QUIT:self.running=False
                if e.type==pygame.MOUSEBUTTONDOWN and e.button==1:self.click(e.pos)
            self.draw(); pygame.display.flip(); self.clock.tick(60)
        pygame.quit()

    def start_solo(self):
        players=[PlayerState(self.human_id,"Você"),PlayerState("bot1","Bot Vórtex",is_bot=True)]
        self.engine=GameEngine(players); self.engine.start(); self.scene="game"; self._run_bots()

    def click(self,pos):
        x,y=pos
        if self.scene=="menu":
            if 470<=x<=810 and 320<=y<=380:self.start_solo()
            elif 470<=x<=810 and 395<=y<=455:self.running=False
            return
        if not self.engine or self.engine.winner_id:
            if 20<=x<=180 and 20<=y<=65:self.scene="menu"
            return
        if self.engine.current_player.player_id!=self.human_id:return
        human=self.engine.current_player
        w,h=self.screen.get_size(); card_w=90; gap=18; total=len(human.hand)*(card_w+gap)-gap; start=max(20,(w-total)//2)
        if h-160<=y<=h-35:
            idx=(x-start)//(card_w+gap)
            if 0<=idx<len(human.hand):
                card=human.hand[idx]
                try:
                    chosen=CardColor.BLUE if card.kind in (CardKind.WILD,CardKind.WILD_DRAW_FOUR) else None
                    self.engine.play_card(self.human_id,card.card_id,chosen); self._run_bots()
                except RuleError:pass
        if w-180<=x<=w-30 and h//2-30<=y<=h//2+30:
            try:
                c=self.engine.draw_for_turn(self.human_id)
                if not self.engine.is_playable(c): self.engine.end_turn(self.human_id); self._run_bots()
            except RuleError:pass

    def _run_bots(self):
        guard=0
        while self.engine and not self.engine.winner_id and self.engine.current_player.is_bot and guard<20:
            guard+=1; p=self.engine.current_player; card,color=self.bot.choose(self.engine,p)
            if card:self.engine.play_card(p.player_id,card.card_id,color)
            else:
                drawn=self.engine.draw_for_turn(p.player_id)
                if self.engine.is_playable(drawn):
                    color=self.bot.choose(self.engine,p)[1] if drawn.kind in (CardKind.WILD,CardKind.WILD_DRAW_FOUR) else None
                    self.engine.play_card(p.player_id,drawn.card_id,color)
                else:self.engine.end_turn(p.player_id)

    def draw_card(self,rect,card,hidden=False):
        pygame.draw.rect(self.screen,(35,38,70) if hidden else COLORS.get(card.color,(90,55,145)),rect,border_radius=14)
        pygame.draw.rect(self.screen,(245,245,255),rect,2,border_radius=14)
        label="V" if hidden else card.display_name
        surf=self.font.render(label,True,TEXT); self.screen.blit(surf,surf.get_rect(center=rect.center))

    def draw(self):
        self.screen.fill(BG); w,h=self.screen.get_size()
        if self.scene=="menu":
            title=self.big.render("VORTEX CARDS",True,TEXT);self.screen.blit(title,title.get_rect(center=(w//2,190)))
            sub=self.font.render("Energia, estratégia e caos controlado",True,MUTED);self.screen.blit(sub,sub.get_rect(center=(w//2,245)))
            for rect,label in [(pygame.Rect(w//2-170,320,340,60),"Jogar contra IA"),(pygame.Rect(w//2-170,395,340,60),"Sair")]:
                pygame.draw.rect(self.screen,ACCENT,rect,border_radius=16); s=self.font.render(label,True,TEXT); self.screen.blit(s,s.get_rect(center=rect.center))
            return
        e=self.engine
        back=pygame.Rect(20,20,160,45);pygame.draw.rect(self.screen,PANEL,back,border_radius=10);self.screen.blit(self.font.render("← Menu",True,TEXT),(42,29))
        if e.winner_id:
            winner=next(p for p in e.players if p.player_id==e.winner_id)
            t=self.big.render(f"{winner.name} venceu!",True,TEXT);self.screen.blit(t,t.get_rect(center=(w//2,h//2)))
            return
        top=pygame.Rect(w//2-55,h//2-85,110,160);self.draw_card(top,e.top_card)
        col=e.active_color.value if e.active_color else "-"; info=self.font.render(f"Cor ativa: {col}  •  Direção: {'↻' if e.direction==1 else '↺'}",True,TEXT);self.screen.blit(info,info.get_rect(center=(w//2,h//2-120)))
        button=pygame.Rect(w-180,h//2-30,150,60);pygame.draw.rect(self.screen,ACCENT if e.current_player.player_id==self.human_id else PANEL,button,border_radius=12);self.screen.blit(self.font.render("Comprar",True,TEXT),self.font.render("Comprar",True,TEXT).get_rect(center=button.center))
        human=next(p for p in e.players if p.player_id==self.human_id); card_w=90;gap=18;total=len(human.hand)*(card_w+gap)-gap;start=max(20,(w-total)//2)
        for i,c in enumerate(human.hand):self.draw_card(pygame.Rect(start+i*(card_w+gap),h-160,card_w,125),c)
        enemy=next(p for p in e.players if p.player_id!=self.human_id); self.screen.blit(self.font.render(f"{enemy.name}: {len(enemy.hand)} cartas",True,TEXT),(w//2-100,80))
        turn=self.font.render(f"Turno: {e.current_player.name}",True,TEXT);self.screen.blit(turn,(30,90))
