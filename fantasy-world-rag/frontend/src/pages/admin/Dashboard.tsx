import { useEffect } from 'react'
import { motion } from 'framer-motion'
import { Users, MessageCircle, Database, TrendingUp } from 'lucide-react'
import { Card } from '@/components/common'
import { useCharacterStore } from '@/stores'

export default function AdminDashboard() {
  const { characters, fetchCharacters } = useCharacterStore()

  useEffect(() => {
    fetchCharacters()
  }, [fetchCharacters])

  const stats = [
    {
      title: 'Personaggi Totali',
      value: characters.length,
      icon: Users,
      color: 'from-blue-500 to-cyan-500'
    },
    {
      title: 'Personaggi Attivi',
      value: characters.filter(c => c.is_active).length,
      icon: MessageCircle,
      color: 'from-green-500 to-emerald-500'
    },
    {
      title: 'Knowledge Entries',
      value: '~1.2k',
      icon: Database,
      color: 'from-purple-500 to-pink-500'
    },
    {
      title: 'Chat Sessions',
      value: '324',
      icon: TrendingUp,
      color: 'from-orange-500 to-amber-500'
    }
  ]

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-fantasy text-white mb-2">Dashboard</h1>
        <p className="text-gray-400">Panoramica del sistema Fantasy World RAG</p>
      </div>

      {/* Stats Grid */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: index * 0.1 }}
          >
            <Card variant="glass" className="p-6">
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-gray-400 mb-1">{stat.title}</p>
                  <p className="text-3xl font-bold text-white">{stat.value}</p>
                </div>
                <div className={`p-3 rounded-lg bg-gradient-to-br ${stat.color}`}>
                  <stat.icon className="w-6 h-6 text-white" />
                </div>
              </div>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Recent Characters */}
      <Card variant="glass" className="p-6">
        <h2 className="text-xl font-fantasy text-white mb-4">Personaggi Recenti</h2>
        
        {characters.length > 0 ? (
          <div className="space-y-3">
            {characters.slice(0, 5).map(character => (
              <div 
                key={character.id}
                className="flex items-center gap-4 p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
              >
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-fantasy-accent to-fantasy-gold flex items-center justify-center shrink-0">
                  <span className="font-fantasy text-fantasy-darker">
                    {character.name.charAt(0)}
                  </span>
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-medium text-white truncate">{character.name}</h3>
                  <p className="text-sm text-gray-400 truncate">
                    {character.race} {character.class_type && `• ${character.class_type}`}
                  </p>
                </div>
                <span className={`px-2 py-1 rounded text-xs ${
                  character.is_active 
                    ? 'bg-green-900/30 text-green-400' 
                    : 'bg-gray-800 text-gray-400'
                }`}>
                  {character.is_active ? 'Attivo' : 'Inattivo'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-center py-8">
            Nessun personaggio creato. Vai a "Characters" per crearne uno nuovo.
          </p>
        )}
      </Card>

      {/* Quick Actions */}
      <div className="grid sm:grid-cols-2 gap-6">
        <Card variant="glass" className="p-6">
          <h3 className="font-fantasy text-white mb-2">Crea Personaggio</h3>
          <p className="text-gray-400 text-sm mb-4">
            Usa l'editor avanzato con supporto AI per creare nuovi personaggi.
          </p>
          <a 
            href="/admin/characters/new"
            className="inline-flex items-center gap-2 text-fantasy-accent hover:text-fantasy-gold transition-colors"
          >
            Vai all'editor →
          </a>
        </Card>

        <Card variant="glass" className="p-6">
          <h3 className="font-fantasy text-white mb-2">Knowledge Base</h3>
          <p className="text-gray-400 text-sm mb-4">
            Gestisci la knowledge base del mondo fantasy per risposte migliori.
          </p>
          <a 
            href="/admin/knowledge"
            className="inline-flex items-center gap-2 text-fantasy-accent hover:text-fantasy-gold transition-colors"
          >
            Gestisci knowledge →
          </a>
        </Card>
      </div>
    </div>
  )
}
