package com.dairydash.ui.farmers

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.dairydash.data.db.FarmerEntity
import com.dairydash.databinding.ItemFarmerBinding

class FarmerAdapter(
    private val onDeleteClick: (FarmerEntity) -> Unit
) : ListAdapter<FarmerEntity, FarmerAdapter.FarmerViewHolder>(DIFF_CALLBACK) {

    private var fullList: List<FarmerEntity> = emptyList()

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): FarmerViewHolder {
        val binding = ItemFarmerBinding.inflate(LayoutInflater.from(parent.context), parent, false)
        return FarmerViewHolder(binding)
    }

    override fun onBindViewHolder(holder: FarmerViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    fun setFullList(list: List<FarmerEntity>) {
        fullList = list
        submitList(list)
    }

    fun filter(query: String) {
        val filtered = if (query.isBlank()) {
            fullList
        } else {
            fullList.filter {
                it.farmerId.contains(query, ignoreCase = true) ||
                it.name.contains(query, ignoreCase = true) ||
                it.phone.contains(query, ignoreCase = true)
            }
        }
        submitList(filtered)
    }

    inner class FarmerViewHolder(private val binding: ItemFarmerBinding) :
        RecyclerView.ViewHolder(binding.root) {

        fun bind(farmer: FarmerEntity) {
            binding.tvFarmerId.text = farmer.farmerId
            binding.tvFarmerName.text = farmer.name
            binding.tvFarmerPhone.text = farmer.phone
            binding.tvFarmerInfo.text =
                "${farmer.cows} Cows / ${farmer.buffaloes} Buffaloes · ${farmer.dailySupply}L/day"
            binding.btnDelete.setOnClickListener { onDeleteClick(farmer) }
        }
    }

    companion object {
        private val DIFF_CALLBACK = object : DiffUtil.ItemCallback<FarmerEntity>() {
            override fun areItemsTheSame(old: FarmerEntity, new: FarmerEntity) =
                old.farmerId == new.farmerId
            override fun areContentsTheSame(old: FarmerEntity, new: FarmerEntity) =
                old == new
        }
    }
}
