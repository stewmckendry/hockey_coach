'use client'

/**
 * Sidebar component for future navigation features
 * Currently a placeholder for future implementation
 */
export function Sidebar() {
  return (
    <aside className="hidden lg:flex flex-col w-64 bg-white border-r border-neutral-200">
      <div className="p-4">
        <h2 className="text-sm font-semibold text-neutral-900 mb-4">
          Quick Actions
        </h2>
        
        {/* TODO: Add quick action buttons */}
        <div className="space-y-2">
          <div className="text-xs text-neutral-500">
            Coming Soon:
          </div>
          <div className="text-sm text-neutral-400">
            • New Practice Plan
          </div>
          <div className="text-sm text-neutral-400">
            • Player Assessment
          </div>
          <div className="text-sm text-neutral-400">
            • Season Planning
          </div>
          <div className="text-sm text-neutral-400">
            • Knowledge Search
          </div>
        </div>
      </div>

      <div className="p-4 border-t border-neutral-200 mt-auto">
        <div className="text-xs text-neutral-500">
          Need help getting started?
        </div>
        <div className="text-sm text-hockey-blue mt-1">
          Try asking: "Create a practice plan for U14 players"
        </div>
      </div>
    </aside>
  )
}

export default Sidebar
