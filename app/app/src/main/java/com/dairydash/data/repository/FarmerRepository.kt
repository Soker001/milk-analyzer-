package com.dairydash.data.repository

import androidx.lifecycle.LiveData
import com.dairydash.data.db.FarmerDao
import com.dairydash.data.db.FarmerEntity

class FarmerRepository(private val farmerDao: FarmerDao) {

    val allFarmers: LiveData<List<FarmerEntity>> = farmerDao.getAllFarmers()

    suspend fun insertFarmer(farmer: FarmerEntity) {
        farmerDao.insertFarmer(farmer)
    }

    suspend fun deleteFarmer(farmer: FarmerEntity) {
        farmerDao.deleteFarmer(farmer)
    }

    suspend fun getAllFarmersList(): List<FarmerEntity> {
        return farmerDao.getAllFarmersList()
    }
}
