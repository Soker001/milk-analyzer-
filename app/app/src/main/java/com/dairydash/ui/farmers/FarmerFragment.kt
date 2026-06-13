package com.dairydash.ui.farmers

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.core.widget.addTextChangedListener
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.recyclerview.widget.DividerItemDecoration
import androidx.recyclerview.widget.LinearLayoutManager
import com.dairydash.databinding.FragmentFarmerBinding

class FarmerFragment : Fragment() {

    private var _binding: FragmentFarmerBinding? = null
    private val binding get() = _binding!!
    private val viewModel: FarmerViewModel by viewModels()
    private lateinit var adapter: FarmerAdapter

    override fun onCreateView(
        inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?
    ): View {
        _binding = FragmentFarmerBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupRecyclerView()
        observeData()
        setupListeners()
    }

    private fun setupRecyclerView() {
        adapter = FarmerAdapter { farmer ->
            AlertDialog.Builder(requireContext())
                .setTitle("Confirm Delete")
                .setMessage("Are you sure you want to delete ${farmer.name}?")
                .setPositiveButton("Delete") { _, _ -> viewModel.deleteFarmer(farmer) }
                .setNegativeButton("Cancel", null)
                .show()
        }
        binding.rvFarmers.layoutManager = LinearLayoutManager(requireContext())
        binding.rvFarmers.adapter = adapter
        binding.rvFarmers.addItemDecoration(
            DividerItemDecoration(requireContext(), DividerItemDecoration.VERTICAL)
        )
    }

    private fun observeData() {
        viewModel.allFarmers.observe(viewLifecycleOwner) { farmers ->
            adapter.setFullList(farmers)
            binding.tvEmpty.visibility = if (farmers.isEmpty()) View.VISIBLE else View.GONE
        }

        viewModel.uiEvent.observe(viewLifecycleOwner) { event ->
            val parts = event.split(":", limit = 2)
            val type = parts[0]
            val msg = parts.getOrElse(1) { event }
            when (type) {
                "SUCCESS" -> {
                    showToast(msg)
                    if (msg.contains("added")) clearForm()
                }
                "ERROR" -> showToast(msg, isError = true)
            }
        }
    }

    private fun setupListeners() {
        binding.btnSaveFarmer.setOnClickListener { saveFarmer() }

        binding.etSearch.addTextChangedListener {
            adapter.filter(it?.toString() ?: "")
        }
    }

    private fun saveFarmer() {
        val farmerId = binding.etFarmerId.text?.toString() ?: ""
        val name = binding.etFarmerName.text?.toString() ?: ""
        val phone = binding.etPhone.text?.toString() ?: ""
        val address = binding.etAddress.text?.toString() ?: ""
        val cows = binding.etCows.text?.toString()?.toIntOrNull() ?: 0
        val buffaloes = binding.etBuffaloes.text?.toString()?.toIntOrNull() ?: 0
        val bank = binding.etBank.text?.toString() ?: ""
        val center = binding.etCenter.text?.toString() ?: ""
        val supply = binding.etSupply.text?.toString()?.toDoubleOrNull() ?: 0.0

        viewModel.addFarmer(farmerId, name, phone, address, cows, buffaloes, bank, center, supply)
    }

    private fun clearForm() {
        binding.etFarmerId.text?.clear()
        binding.etFarmerName.text?.clear()
        binding.etPhone.text?.clear()
        binding.etAddress.text?.clear()
        binding.etCows.setText("0")
        binding.etBuffaloes.setText("0")
        binding.etBank.text?.clear()
        binding.etCenter.text?.clear()
        binding.etSupply.setText("0")
    }

    private fun showToast(msg: String, isError: Boolean = false) {
        Toast.makeText(requireContext(), msg, Toast.LENGTH_SHORT).show()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
