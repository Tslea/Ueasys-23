import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Plus, 
  Search, 
  Edit2, 
  Trash2, 
  MoreVertical,
  Eye,
  MessageCircle,
  Brain
} from 'lucide-react'
import { Card, Button, Input, Modal, Badge } from '@/components/common'
import { useCharacterStore, Character } from '@/stores'
import { cn, formatDate } from '@/lib/utils'

export default function CharactersList() {
  const { characters, fetchCharacters, deleteCharacter, isLoading } = useCharacterStore()
  
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedRace, setSelectedRace] = useState<string | null>(null)
  const [deleteModal, setDeleteModal] = useState<Character | null>(null)
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    fetchCharacters()
  }, [fetchCharacters])

  // Get unique archetypes for filter
  const archetypes = [...new Set(characters.map(c => c.archetype).filter(Boolean))]

  // Filter characters
  const filteredCharacters = characters.filter(character => {
    const matchesSearch = character.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         character.description?.toLowerCase().includes(searchQuery.toLowerCase())
    const matchesArchetype = !selectedRace || character.archetype === selectedRace
    return matchesSearch && matchesArchetype
  })

  const handleDelete = async () => {
    if (!deleteModal) return
    
    setIsDeleting(true)
    try {
      await deleteCharacter(deleteModal.id)
      setDeleteModal(null)
    } catch {
      // Error handled by store
    } finally {
      setIsDeleting(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-fantasy text-white mb-2">Personaggi</h1>
          <p className="text-gray-400">
            Gestisci i personaggi del mondo fantasy ({characters.length} totali)
          </p>
        </div>
        <Link to="/admin/characters/new">
          <Button className="gap-2">
            <Plus className="w-4 h-4" />
            Nuovo Personaggio
          </Button>
        </Link>
      </div>

      {/* Filters */}
      <Card variant="glass" className="p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <Input
              placeholder="Cerca personaggi..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              icon={<Search className="w-5 h-5" />}
            />
          </div>
          
          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => setSelectedRace(null)}
              className={cn(
                'px-3 py-2 rounded-lg text-sm font-medium transition-all',
                !selectedRace 
                  ? 'bg-fantasy-accent text-fantasy-darker' 
                  : 'bg-white/5 text-gray-400 hover:text-white'
              )}
            >
              Tutti
            </button>
            {archetypes.map(archetype => (
              <button
                key={archetype}
                onClick={() => setSelectedRace(archetype)}
                className={cn(
                  'px-3 py-2 rounded-lg text-sm font-medium transition-all capitalize',
                  selectedRace === archetype 
                    ? 'bg-fantasy-accent text-fantasy-darker' 
                    : 'bg-white/5 text-gray-400 hover:text-white'
                )}
              >
                {archetype}
              </button>
            ))}
          </div>
        </div>
      </Card>

      {/* Characters Grid */}
      {isLoading ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <Card key={i} className="h-48 animate-pulse bg-white/5" />
          ))}
        </div>
      ) : filteredCharacters.length > 0 ? (
        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          <AnimatePresence>
            {filteredCharacters.map((character, index) => (
              <motion.div
                key={character.id}
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.95 }}
                transition={{ duration: 0.3, delay: index * 0.05 }}
              >
                <CharacterCard 
                  character={character} 
                  onDelete={() => setDeleteModal(character)}
                />
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      ) : (
        <Card variant="glass" className="p-12 text-center">
          <div className="w-16 h-16 rounded-full bg-gray-800 flex items-center justify-center mx-auto mb-4">
            <Search className="w-8 h-8 text-gray-600" />
          </div>
          <h3 className="text-xl text-white mb-2">Nessun Risultato</h3>
          <p className="text-gray-400 mb-6">
            {searchQuery || selectedRace 
              ? 'Prova a modificare i filtri di ricerca'
              : 'Non ci sono ancora personaggi. Creane uno nuovo!'}
          </p>
          {!searchQuery && !selectedRace && (
            <Link to="/admin/characters/new">
              <Button>Crea Personaggio</Button>
            </Link>
          )}
        </Card>
      )}

      {/* Delete Confirmation Modal */}
      <Modal
        isOpen={!!deleteModal}
        onClose={() => setDeleteModal(null)}
        title="Elimina Personaggio"
      >
        <div className="space-y-4">
          <p className="text-gray-300">
            Sei sicuro di voler eliminare <strong className="text-white">{deleteModal?.name}</strong>?
            Questa azione non può essere annullata.
          </p>
          <div className="flex gap-3 justify-end">
            <Button variant="ghost" onClick={() => setDeleteModal(null)}>
              Annulla
            </Button>
            <Button 
              variant="danger" 
              onClick={handleDelete}
              isLoading={isDeleting}
            >
              Elimina
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  )
}

function CharacterCard({ 
  character, 
  onDelete 
}: { 
  character: Character
  onDelete: () => void 
}) {
  const [showMenu, setShowMenu] = useState(false)

  return (
    <Card variant="glass" className="group overflow-hidden">
      {/* Header with Avatar */}
      <div className="h-24 bg-gradient-to-br from-fantasy-accent/20 to-fantasy-gold/10 relative">
        {character.avatar_url ? (
          <img 
            src={character.avatar_url} 
            alt={character.name}
            className="w-full h-full object-cover"
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-fantasy-accent to-fantasy-gold flex items-center justify-center">
              <span className="text-2xl font-fantasy text-fantasy-darker">
                {character.name.charAt(0)}
              </span>
            </div>
          </div>
        )}
        <div className="absolute inset-0 bg-gradient-to-t from-fantasy-dark to-transparent" />
        
        {/* Menu Button */}
        <div className="absolute top-2 right-2">
          <div className="relative">
            <button
              onClick={() => setShowMenu(!showMenu)}
              className="p-2 rounded-lg bg-black/50 text-white hover:bg-black/70 transition-colors"
            >
              <MoreVertical className="w-4 h-4" />
            </button>
            
            {showMenu && (
              <>
                <div 
                  className="fixed inset-0 z-10" 
                  onClick={() => setShowMenu(false)} 
                />
                <div className="absolute right-0 top-full mt-1 w-40 py-1 rounded-lg bg-fantasy-dark border border-gray-700 shadow-xl z-20">
                  <Link
                    to={`/chat/${character.id}`}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5"
                  >
                    <MessageCircle className="w-4 h-4" />
                    Chatta
                  </Link>
                  <Link
                    to={`/admin/characters/${character.id}`}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5"
                  >
                    <Eye className="w-4 h-4" />
                    Visualizza
                  </Link>
                  <Link
                    to={`/admin/characters/${character.id}/edit`}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-white/5"
                  >
                    <Edit2 className="w-4 h-4" />
                    Modifica
                  </Link>
                  <Link
                    to={`/admin/characters/${character.id}/knowledge`}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-neon-purple hover:text-neon-blue hover:bg-neon-purple/10"
                  >
                    <Brain className="w-4 h-4" />
                    Conoscenza
                  </Link>
                  <button
                    onClick={() => {
                      setShowMenu(false)
                      onDelete()
                    }}
                    className="flex items-center gap-2 px-3 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-red-900/20 w-full"
                  >
                    <Trash2 className="w-4 h-4" />
                    Elimina
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Status Badge */}
        <div className="absolute bottom-2 left-2">
          <Badge variant={character.status === 'active' ? 'success' : 'secondary'}>
            {character.status === 'active' ? 'Attivo' : 'Inattivo'}
          </Badge>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        <div className="mb-2">
          <h3 className="font-fantasy text-lg text-white group-hover:text-fantasy-gold transition-colors">
            {character.name}
          </h3>
          <p className="text-sm text-fantasy-accent capitalize">
            {character.archetype} • {character.alignment?.replace('_', ' ')}
          </p>
        </div>
        
        <p className="text-sm text-gray-400 line-clamp-2 mb-3">
          {character.description || 'Nessuna descrizione'}
        </p>

        {/* Traits Preview */}
        {character.personality?.traits && character.personality.traits.length > 0 && (
          <div className="flex gap-1 flex-wrap mb-3">
            {character.personality.traits.slice(0, 3).map((trait: string, i: number) => (
              <span 
                key={i}
                className="px-2 py-0.5 rounded text-xs bg-white/5 text-gray-400"
              >
                {trait}
              </span>
            ))}
            {character.personality.traits.length > 3 && (
              <span className="px-2 py-0.5 rounded text-xs bg-white/5 text-gray-500">
                +{character.personality.traits.length - 3}
              </span>
            )}
          </div>
        )}

        {/* Footer */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-800">
          <span className="text-xs text-gray-500">
            {formatDate(character.updated_at)}
          </span>
          <Link
            to={`/admin/characters/${character.id}/edit`}
            className="text-sm text-fantasy-accent hover:text-fantasy-gold transition-colors"
          >
            Modifica →
          </Link>
        </div>
      </div>
    </Card>
  )
}
