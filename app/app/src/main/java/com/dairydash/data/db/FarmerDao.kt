package com.dairydash.data.db

import androidx.lifecycle.LiveData
import androidx.room.*

@Dao
interface FarmerDao {

    @Query("SELECT * FROM farmers ORDER BY farmerId ASC")
    fun getAllFarmers(): LiveData<List<FarmerEntity>>

    @Query("SELECT * FROM farmers ORDER BY farmerId ASC")
    suspend fun getAllFarmersList(): List<FarmerEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertFarmer(farmer: FarmerEntity)

    @Delete
    suspend fun deleteFarmer(farmer: FarmerEntity)

    @Query("SELECT * FROM farmers WHERE farmerId = :id")
    suspend fun getFarmerById(id: String): FarmerEntity?
}
